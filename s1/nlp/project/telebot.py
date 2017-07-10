# -*- coding: UTF-8 -*-
from collections import OrderedDict
import numpy as np
import pprint
import time
import apiai
import json

from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, create_open, pave_event_space
from telepot.namedtuple import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from collections import defaultdict

import mariaDB

import telepot
import telepot.loop
import random
from util import DomainDetectionFail, ModalityDetectionFail, RelationDetectionFail, FailToAnswerException

from enum import Enum


class Modality(Enum):
    querying = 1
    enriching = 2


MANUEL_ID = 45571984
CLIENT_ACCESS_TOKEN = 'bbb35a4d419f48ee84ae9800be4768f6'

user_handler = {}

domain_vectors = {}
with open("BabelDomains_full/domain_vectors.txt") as fin:
    for row in fin:
        row = row[:-2].split("\t")
        domain = row.pop(0)
        domain_vectors[domain] = {}
        for dim in row:
            name, value = dim.split(" ")
            domain_vectors[domain][name] = float(value)

spacy_classifier = spacy.load("en_core_web_md")


class MariaBot(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        if args or kwargs:
            super(MariaBot, self).__init__(*args, **kwargs)
            self.db = mariaDB.gaia_db()
        else:
            self.db = mariaDB.fake_db()

            def print_msg(user_tid, msg, reply_markup=None):
                print("[SENDING MESSAGE] >>>>> {}".format(msg))

            self.sendMessage = print_msg

        self.user_tid = None
        self.domain = None
        self.relation = None
        self.modality = None

    def log_message(self, msg):
        self.sendMessage(MANUEL_ID, pprint.pformat(msg))

    def sendMessage(self, user_id, msg, reply_markup=None):
        self.bot.sendMessage(user_id, msg, reply_markup=reply_markup)

    def get_open_question(self, msg):
        raise NotImplementedError()

    @staticmethod
    def classify_modality(msg_txt):
        if "?" == msg_txt[-1]:
            return Modality.querying
        if "?" in msg_txt:
            raise ModalityDetectionFail()
        else:
            return Modality.enriching

    def offer_user_options(self, original_msg, answer_type, options, query_msg):
        keyboard_layout = []
        for option in options:
            keyboard_layout.append(KeyboardButton(text=option))
        keyboard = ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True,
            keyboard=keyboard_layout)

        def query_response_handler(msg):
            markup = ReplyKeyboardRemove()
            employee_id = msg['from']['id']
            self.sendMessage(employee_id, "Ok, got it", reply_markup=markup)
            answer = msg['text']
            if answer_type == "domain":
                print("[BOT] setting domain to: ", answer)
                self.domain = answer
            elif answer_type == "relation":
                self.relation = answer
                print("[BOT] setting relation to: ", answer)
            del user_handler[self.user_tid]
            self.on_message(original_msg)

        user_handler[self.user_tid] = query_response_handler
        self.sendMessage(self.user_tid, query_msg, reply_markup=keyboard)

    @staticmethod
    def classify_domain(msg_txt):
        # raise DomainDetectionFail()
        with open("BabelDomains_full/domain_list.txt") as fin:
            possible_domains = fin.read()[:-1].split("\n")

        classified_domains = OrderedDict({d: 0 for d in possible_domains})
        for word in msg_txt.split(" "):  # nltk tokenize
            for d in possible_domains:
                try:
                    classified_domains[d] += domain_vectors[d][word]
                except KeyError:
                    pass
                else:
                    print("adding weight domain:", d, "word:", word, "weight", domain_vectors[d][word])
        result = sorted(classified_domains, key=lambda x: classified_domains[x], reverse=True)
        best_guess = result[0]
        print("best guess", best_guess, classified_domains[best_guess])
        if classified_domains[best_guess] < 10:  # HYPER PARAM
            raise DomainDetectionFail()
        return best_guess

    @staticmethod
    def check_for_open_question_answer(user_msg_txt, domain):
        if random.random() < 0.4:
            return "42"
        return False

    @staticmethod
    def answer_question(user_msg_txt, domain, relation):
        # requests all the answer for domain
        # offer a list of possible answers
        raise FailToAnswerException()

    @staticmethod
    def infer_question_relation(question_txt, domain):
        with open("chatbot_maps/domains_to_relations.tsv") as fin:
            possible_relations = {r.split("\t")[0]: r.split("\t")[1:] for r in fin.read().split("\n")}[domain]
        # babelify text
        guesses = []
        # stem stuff
        for possible_relation in possible_relations:
            if possible_relation in question_txt:
                guesses.append(possible_relation)
        # TODO: offer a distribution of relations
        if not guesses:
            raise RelationDetectionFail()
        else:
            best_guess = random.choice(guesses)
        return best_guess

    def analyze_request(self, msg_txt):
        pass

    @staticmethod
    def is_greeting(user_msg_txt):
        msg_bow = set(user_msg_txt.split(" "))
        GREETING_BOW = {"hello", "hi", "greetings", "sup", "what's up", }
        return len(msg_bow.intersection(GREETING_BOW)) != 0

    def on_message(self, msg):
        global user_handler

        message_user_tid = msg['from']['id']
        if not self.user_tid:
            self.user_tid = message_user_tid
        else:
            assert message_user_tid == self.user_tid

        user = self.db.find_by_tid(message_user_tid)

        if user is None:  # if user is a new user
            self.register_user(message_user_tid, msg)
            return

        elif user.tid in user_handler:
            print(user.tid, "was redirected by handler")
            return user_handler[user.tid](msg)

        try:
            user_msg_txt = msg['text']
        except KeyError:
            self.log_message("failed to parse the message")
            self.log_message(msg)
            self.sendMessage(user.tid, "i failed to understand that; admin noticed")
            return

        if self.is_greeting(user_msg_txt):
            self.greet_user(user)
            return

        if not self.domain:
            try:
                self.domain = self.classify_domain(user_msg_txt)
            except DomainDetectionFail:
                with open("BabelDomains_full/domain_list.txt") as fin:
                    possible_domains = fin.read()[:-1].split("\n")
                self.offer_user_options(msg, "domain", possible_domains, "what's the domain?")
            else:
                self.on_message(msg)
            return

        if not self.modality:
            try:
                self.modality = self.classify_modality(user_msg_txt)
            except ModalityDetectionFail:
                self.offer_user_options(msg, "modality", ["ask questions", "answer stuff"], "what do you want to do?")
            else:
                print("[BOT] setting modality to: ", self.modality)
                self.on_message(msg)
            return

        if self.modality == Modality.enriching:
            try:
                relation, question = self.db.get_open_question(self.domain)
            except IndexError:
                relation, question = "place", "where is the lalalala"
            # pick a random question
            # ask question to user
            # update KB
            self.db.close_open_question(relation, question)

        elif self.modality == Modality.querying:
            if not self.relation:
                # babelify question
                try:
                    self.relation = self.infer_question_relation(user_msg_txt, self.domain)
                except RelationDetectionFail:
                    self.offer_user_options(msg, "relation", ["relation1", "relation2"], "what's the relation here?")
                    return
            # mumble mumble
            # mumble mumble
            # mumble mumble
            # mumble mumble
            try:
                answer = self.answer_question(user_msg_txt, self.domain, self.relation)
            except FailToAnswerException:
                # ask another user
                self.db.add_open_question(user_msg_txt)
                timeleft = 15
                answer = "something broke; call Manuel"
                while timeleft > 0:
                    user_answer = self.check_for_open_question_answer(user_msg_txt, self.domain)
                    if user_answer:
                        answer = user_answer
                        break
                    self.sendMessage(self.user_tid, "mumble {}".format(timeleft))
                    time.sleep(1)
                    timeleft -= 1

                if timeleft == 0:
                    answer = "i don't know"

            # apply emotive state
            self.sendMessage(self.user_tid, answer)
            self.domain = None
            self.modality = None
            self.relation = None
        else:
            print("skipping", user_msg_txt)

    def register_user(self, message_user_tid, msg):
        global user_handler

        def handle_user_rename(msg):
            # update user object
            user = self.db.find_by_tid(msg['from']['id'])

            user.name = msg['text'].lower()
            self.db.update_one(user)

            del user_handler[message_user_tid]
            self.sendMessage(message_user_tid, "Cool, {}. go ahead ask me something".format(user.name))

        def should_i_use_this_name(msg):
            msg_txt = msg['text']
            parameters, action, response = self.analyze_request(msg_txt)

            if action == "negative":
                user_handler[message_user_tid] = handle_user_rename
                self.sendMessage(message_user_tid, "how should i call you then?")
            elif action == "positive":
                handle_user_rename({'text': msg['from']['first_name']})
            else:
                self.sendMessage(message_user_tid, "wut?")

        user_handler[message_user_tid] = should_i_use_this_name
        self.db.insert_one({'tid': message_user_tid})
        self.sendMessage(message_user_tid, "Hello {}, may i address you as {}?".format(
            msg['from']['first_name'],
            msg['from']['first_name'])
                         )

    def greet_user(self, user):
        GREETING_RESPONSES = ["hello", "hi", "greetings", "sup", "what's up", ]
        self.sendMessage(user.tid, random.choice(GREETING_RESPONSES))
        self.sendMessage(user.tid, "ask away")

    def parse_user_msg(self, text):
        self.parse_pos(text)
        return "input.unknown"


def main():
    with open("api_key") as fin:
        KEY = fin.read()[:-1]
    bot = telepot.DelegatorBot(KEY, [
        pave_event_space()(
            per_chat_id(), create_open, MariaBot, timeout=99999),
    ])
    test_bot = MariaBot()
    test_user_id = random.randint(0, 1000)

    msg_flow = [
        "sup n00b",
        "how does your pussy tastes like?",
        # "animals",
        "relation1"
    ]
    for msg in msg_flow:
        message_template = {'from': {'id': test_user_id, }, 'text': msg}
        print("[USER WRITES]: <<<<< {}".format(message_template['text']))
        test_bot.on_message(message_template)
    for msg in msg_flow:
        message_template = {'from': {'id': test_user_id, }, 'text': msg}
        print("[USER WRITES]: <<<<< {}".format(message_template['text']))
        test_bot.on_message(message_template)
        # MessageLoop(bot).run_forever()


if __name__ == "__main__":
    main()
