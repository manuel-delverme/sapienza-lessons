# -*- coding: UTF-8 -*-
import pprint
import time
import apiai
import json

from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, create_open, pave_event_space
from telepot.namedtuple import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from collections import defaultdict

import gaiaDB

import telepot
import telepot.loop
import random

MANUEL_ID = 45571984
CLIENT_ACCESS_TOKEN = 'bbb35a4d419f48ee84ae9800be4768f6'

user_handler = {}
user_answer = defaultdict(dict)


class MariaBot(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MariaBot, self).__init__(*args, **kwargs)
        self.db = gaiaDB.gaia_db()

    def log_message(self, msg):
        self.bot.sendMessage(MANUEL_ID, pprint.pformat(msg))

    def analyze_request(self, msg_txt):
        ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
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

    def on_message(self, msg):
        global user_handler

        message_user_tid = msg['from']['id']
        user = self.db.find_by_tid(message_user_tid)

        if user is None:  # if user is a new user
            def handle_user_rename(msg):
                # update user object
                user = self.db.find_by_tid(msg['from']['id'])

                user.name = msg['text'].lower()
                self.db.update_one(user)

                del user_handler[message_user_tid]
                self.bot.sendMessage(message_user_tid, "Cool, {}. go ahead ask me something".format(user.name))

            def should_i_use_this_name(msg):
                msg_txt = msg['text']
                parameters, action, response = self.analyze_request(msg_txt)

                if action == "negative":
                    user_handler[message_user_tid] = handle_user_rename
                    self.bot.sendMessage(message_user_tid, "how should i call you then?")
                elif action == "positive":
                    handle_user_rename({'text': msg['from']['first_name']})
                else:
                    self.bot.sendMessage(message_user_tid, "wut?")

            user_handler[message_user_tid] = should_i_use_this_name
            self.db.insert_one({'tid': message_user_tid})
            self.bot.sendMessage(message_user_tid, "Hello {}, may i address you as {}?".format(
                msg['from']['first_name'], msg['from']['first_name']))
            return

        elif user.tid in user_handler:
            print(user.tid, "was redirected by handler")
            return user_handler[user.tid](msg)

        try:
            user_msg_txt = msg['text']
        except KeyError:
            self.log_message("failed to parse the message")
            self.log_message(msg)
            self.bot.sendMessage(user.tid, "i failed to understand that; admin noticed")
            return

        parameters, action, response = self.analyze_request(user_msg_txt)
        self.bot.sendMessage(user.tid, response)

        msg_bow = set(user_msg_txt.split(" "))

        GREETING_BOW = {"hello", "hi", "greetings", "sup", "what's up", }

        if msg_bow.intersection(GREETING_BOW) or action == "greeting":
            self.greet_user(user)

        elif action == 'place':
            print("got:", action)
        else:
            print("skipping", action)

    def greet_user(self, user):
        GREETING_RESPONSES = {"hello", "hi", "greetings", "sup", "what's up", }
        self.bot.sendMessage(user.tid, random.choice(GREETING_RESPONSES))

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
    MessageLoop(bot).run_forever()


if __name__ == "__main__":
    main()
