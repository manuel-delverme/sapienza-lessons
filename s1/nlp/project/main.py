# -*- coding: UTF-8 -*-
import json
import logging
import pickle
import pprint
import random
import collections
import apiai
import nltk
import telepot
import telepot.loop
import telepot.loop
from telepot.delegate import per_chat_id, create_open, pave_event_space
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup

import answer_question
import classify_pattern
import config
import mariaDB
import commons

user_handler = {}

domain_vectors = {}
try:
    with open("cache/domain_vectors.pkl", "rb") as fin:
        domain_vectors = pickle.load(fin)
except FileNotFoundError:
    with open("BabelDomains_full/domain_vectors.txt") as fin:
        for row in fin:
            row = row[:-2].split("\t")
            domain = row.pop(0)
            domain_vectors[domain] = {}
            for dim in row:
                name, value = dim.split(" ")
                domain_vectors[domain][name] = float(value)
    with open("cache/domain_vectors.pkl", "wb") as fout:
        pickle.dump(domain_vectors, fout)


class MariaBot(telepot.helper.ChatHandler):
    _GREETING_RESPONSES = ["hello", "hi", "greetings", "sup", "what's up", ]

    def __init__(self, *args, **kwargs):
        self.distracting_user = -1
        self.eliza = None
        logging.debug('MariaBot init')
        self.db = mariaDB.Gaia_db()
        logging.debug('DB up {}:{}'.format(self.db.client.HOST, self.db.client.PORT))
        if 'test_run' in kwargs and kwargs['test_run']:
            # self.db = mariaDB.Fake_db()
            def print_msg(user_tid, msg, reply_markup=None):
                print("[BOT]:[SENDING MESSAGE] >>>>> {}".format(msg))

            self.sendMessage = print_msg
        else:
            super(MariaBot, self).__init__(*args, **kwargs)

        self.user_tid = None
        self.domain = None
        self.relation = None
        self.modality = None

    def log_message(self, msg):
        self.sendMessage(config.MANUEL_ID, "[LOG] " + pprint.pformat(msg))

    def sendMessage(self, user_id, msg, reply_markup=None):
        self.bot.sendMessage(user_id, msg, reply_markup=reply_markup)

    def get_open_question(self, msg):
        raise NotImplementedError()

    @staticmethod
    def classify_modality(msg_txt):
        if "?" == msg_txt[-1]:
            return commons.Modality.querying
        if "?" in msg_txt:
            raise commons.ModalityDetectionFail()
        else:
            return commons.Modality.enriching

    def offer_user_options(self, original_msg, answer_type, options, query_msg):
        keyboard_layout = []
        for idx, option in enumerate(options):
            if idx % 2 == 0:
                keyboard_layout.append([KeyboardButton(text=option)])
            else:
                keyboard_layout[-1].append(KeyboardButton(text=option))

        keyboard = ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True,
            keyboard=keyboard_layout)

        def query_response_handler(msg):
            markup = ReplyKeyboardRemove()
            employee_id = msg['from']['id']
            answer = msg['text']
            if answer not in options:
                self.sendMessage(employee_id, "option not valid, try again")
                return
            self.sendMessage(employee_id, "Ok, got it", reply_markup=markup)

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
        with open("chatbot_maps/domain_list.txt") as fin:
            possible_domains = fin.read()[:-1].split("\n")

        classified_domains = collections.OrderedDict({d: 0 for d in possible_domains})
        for word in nltk.tokenize.word_tokenize(msg_txt):
            # print("[BOT] word:", word, "-" * 100)
            total_weight = 0
            weights = {}

            for d in possible_domains:
                try:
                    weight = domain_vectors[d][word]
                except KeyError:
                    pass
                else:
                    # total_weight += math.log(weight)
                    weights[d] = weight
            if weights:
                for d in weights.keys():
                    classified_domains[d] += weights[d] / (len(weights) ** 2)

        result = sorted(classified_domains, key=lambda x: classified_domains[x], reverse=True)
        best_guess = result[0]
        if classified_domains[best_guess] < 1.5:  # HYPER PARAM
            print("[BOT] domain for question: ", best_guess, classified_domains[best_guess])
            print("[BOT] failed confidence < 1.5")
            raise commons.DomainDetectionFail()
        return best_guess

    @staticmethod
    def check_for_open_question_answer(user_msg_txt, domain):
        if random.random() < 0.4:
            return "42"
        return False

    def answer_question(self, user_msg_txt, domain, relation):
        # print("[BOT] answering question:", user_msg_txt, domain, relation)
        answer = answer_question.answer_question(self.db, user_msg_txt, relation)
        if answer:
            return answer
        raise commons.FailToAnswerException()

    @staticmethod
    def infer_question_relation(question_txt, domain):
        question = nltk.tokenize.word_tokenize(question_txt)
        sno = nltk.stem.SnowballStemmer('english')
        question = [sno.stem(word) for word in question]
        relation = classify_pattern.find_relation(question)
        if not relation:
            raise commons.RelationDetectionFail()
        else:
            return relation

    def analyze_request(self, msg_txt):
        ai = apiai.ApiAI(config.CLIENT_ACCESS_TOKEN)
        request = ai.text_request()
        request.query = msg_txt
        response = request.getresponse()
        reply = response.read()
        reply = reply.decode("utf-8")
        parsed_json = json.loads(reply)
        action = parsed_json['result']['action'].lower()
        parameters = parsed_json['result']['parameters']
        response = parsed_json['result']['fulfillment']['speech']
        return parameters, action, response

    @staticmethod
    def is_greeting(user_msg_txt):
        msg_bow = set(user_msg_txt.split(" "))
        GREETING_BOW = {"hello", "hi", "greetings", "sup", "what's up", }
        return len(msg_bow.intersection(GREETING_BOW)) != 0

    def on_message(self, msg):

        self.user_tid = message_user_tid = msg['from']['id']
        user = self.db.find_by_tid(message_user_tid)
        logging.debug("user_obj := {}".format(user))

        if user is None:  # if user is a new user
            logging.debug("user is new")
            self.register_user(message_user_tid, msg)
        elif user.tid in user_handler:
           logging.debug("{} was redirected by handler".format(user.tid))
           # print(user.tid, "was redirected by handler")
           return user_handler[user.tid](msg)

        try:
            user_msg_txt = msg['text']
        except KeyError:
            logging.warning("failed to parse the message: {}".format(msg))
            self.log_message("failed to parse the message:")
            self.log_message(msg)
            self.sendMessage(user.tid, "i failed to understand that")
            return

        if "DEBUG" == user_msg_txt:
            logging.debug = self.log_message
            logging.debug("DEBUG:ON")
            return

        if self.is_greeting(user_msg_txt):
            logging.debug("is_greeting".format(user_msg_txt))
            self.greet_user(user)
            return

        if self.distracting_user > 0:
            useless_answer = self.chit_chat(user_msg_txt)
            # print("[BOT] distracting user with {}".format(useless_answer))
            if useless_answer is None:
                self.distracting_user = 1
            else:
                self.sendMessage(self.user_tid, useless_answer)
            self.distracting_user -= 1
            return

        if self.distracting_user == 0:
            answer = "about your earlier query.. I don't know how to answer that try to rephrase or check here -> " \
                     "http://lmgtfy.com/?q={}".format(
                self.unk_msg['text'].replace(" ", "+")
            )
            self.sendMessage(self.user_tid, answer)
            self.distracting_user -= 1
            return

        if "ok" in user_msg_txt:
            self.sendMessage(user.tid, "cool")
            return

        logging.debug("classify_domain {}".format(user_msg_txt))
        if self.domain is None:
            try:
                self.domain = self.classify_domain(user_msg_txt)
            except commons.DomainDetectionFail:
                with open("chatbot_maps/domain_list.txt") as fin:
                    possible_domains = fin.read()[:-1].split("\n")
                self.offer_user_options(msg, "domain", possible_domains, "I'm not sure what we are talking about, please "
                                                                         "choose one option from the following")
                return
            else:
                logging.debug("classify_domain rets {}:".format(self.domain))

        logging.debug("classify_modality for: {}".format(user_msg_txt))

        self.modality = self.classify_modality(user_msg_txt)
        # self.offer_user_options(msg, "modality", ["ask questions", "answer stuff"], "what do you want to do?")

        if self.modality == commons.Modality.enriching:
            logging.debug("modality is : enriching; looking for open question")
            try:
                relation, question = self.db.get_open_question(self.domain)
            except IndexError:
                logging.warning("ran out of questions, looking for Neverland")
                relation, question = "place", "where is Neverland?"
                self.sendMessage(message_user_tid, "i already know everything, ask a question")
                self.modality = None
            else:
                # ask question
                logging.debug("got R:{} Q:{} as question".format(relation, question))

                def handle_enriching(msg):
                    self.db.close_open_question(relation, question)
                    del user_handler[message_user_tid]
                    self.sendMessage(message_user_tid, "thakns for the info!".format(user.name))

                user_handler[message_user_tid] = handle_enriching

                self.sendMessage(message_user_tid,
                                 "question: {} ({}). what would you answer to that?".format(question, relation))

        elif self.modality == commons.Modality.querying:
            logging.debug("modality is: querying")
            self.relation = ""
            logging.debug("answering user question Q:{} D:{} R:{}".format(user_msg_txt, self.domain, self.relation))
            answer = answer_question.answer_question(self.db, user_msg_txt, self.relation)
            if answer:
                # apply emotive state
                self.sendMessage(self.user_tid, answer)
                logging.info("answering {} for {}".format(answer, user_msg_txt))
            else:
                logging.warning("could not answer!")
                # ask another user
                logging.info("opening question {}".format(user_msg_txt))
                self.db.add_open_question(user_msg_txt)
                self.distracting_user = 5
                self.unk_msg = msg
                self.on_message(msg)

            self.domain = None
            self.modality = None
            self.relation = None
        else:
            print("skipping", user_msg_txt)
            logging.error("modality unset", user_msg_txt)
            raise Exception("")

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
            elif action in ("positive", "affermative"):
                msg['text'] = msg['from']['first_name']
                handle_user_rename(msg)
            else:
                self.sendMessage(message_user_tid, "wut?")

        user_handler[message_user_tid] = should_i_use_this_name
        self.db.insert_one({'tid': message_user_tid})
        self.sendMessage(message_user_tid, "Hello {}, may i address you as {}?".format(
            msg['from']['first_name'],
            msg['from']['first_name'])
                         )

    def greet_user(self, user):
        self.sendMessage(user.tid, random.choice(self._GREETING_RESPONSES))
        self.sendMessage(user.tid, "ask away")

    def parse_user_msg(self, text):
        self.parse_pos(text)
        return "input.unknown"

    def chit_chat(self, user_msg_txt):
        if self.eliza is None:
            import eliza
            self.eliza = eliza.Eliza()
        return self.eliza.respond(user_msg_txt)


def main(test_run=False):
    with open("sekrets/api_key") as fin:
        KEY = fin.read()[:-1]
    logging.debug('loaded api_key')

    msg_flow = [
        # "sup n00b",
        # "how does your pussy tastes like?",
        # "how does cake tastes like?",
        # "hard cake is the type of truck?",
        # "what is the material of hard cake?",
        # "animals",

        # "Where is Flagstaff Lake located ?",
        # "ok thanks",
        # "Is coliseum located in Rome?",
        "DEBUG",
        "Where is Flagstaff Lake located ?",
        "ok thanks",
        "Is coliseum located in Rome?",
        "What is the capital of France?",
        "How do cakes smell lke?",
        "what is the material of hard cake?",
        "just wondering",
        "die2",
        "die3",
        "die4",
        "i want to enrich",
        # TODO:
        # debug over telegram
        # screenshot conv for report
        # improve report by looking at old ones
        # "What is an example of a symbol?",
    ]
    logging.debug('bot is in test mode:' + str(test_run))
    if test_run:
        test_bot = MariaBot(test_run=test_run)
        test_user_id = 45571984
        for msg in msg_flow:
            message_template = {'from': {'id': test_user_id, }, 'text': msg}
            print("[USER WRITES]: <<<<< {}".format(message_template['text']))
            test_bot.on_message(message_template)
        for msg in msg_flow:
            message_template = {'from': {'id': test_user_id, }, 'text': msg}
            print("[USER WRITES]: <<<<< {}".format(message_template['text']))
            test_bot.on_message(message_template)
    else:
        # import urllib3
        # import telepot.api

        # proxy_url = 'http://localhost:1234/'
        # telepot.api._pools = {
        #     'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
        # }
        # telepot.api._onetime_pool_spec = (
        # urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))

        logging.debug("running DelegatorBot")
        bot = telepot.DelegatorBot(KEY, [
            pave_event_space()(
                per_chat_id(), create_open, MariaBot, timeout=99999),
        ])
        print(bot.getMe())
        # for msg in msg_flow:
        #     print("sending", msg)
        #     subprocess.call(["/opt/tg/bin/telegram-cli", "-W", "-e", "msg @r_maria_bot {}".format(msg)])
        logging.debug("looping forever")
        MessageLoop(bot).run_forever()
        logging.debug("forever has passed?")


if __name__ == "__main__":
    logging.basicConfig(filename='mariabot.log', level=logging.DEBUG)
    # print("hi")
    # test_run = "--test" in os.sys.argv
    test_run = False
    main(test_run=test_run)
