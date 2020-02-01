import json
import string
import difflib
import random
from datetime import datetime
random.seed(datetime.now())

class EmojiParser:
    def __init__(self, slack_client):
        #Grabs the custom emoji list and user list for server
        self.custom_emoji_list = slack_client.api_call("emoji.list")["emoji"]
        self.users_list = slack_client.api_call("users.list")["members"]
        with open("emoji_dict.txt") as json_file:
            self.emoji_dict = json.load(json_file)


    def search_list(self, query_list): #Adds found emoji matches to the result set
        result_set = set()
        for query in query_list:
            result_set.add(self.find_query(query))
        return result_set

    def format_text(self, message): #Lowercases the message and removes certain punctuation
        formatted_message = message.lower()
        for char in string.punctuation:
            if char not in ['_', ':', '(', ')', '&', ';']:
                formatted_message = formatted_message.replace(char, ' ')
        print(formatted_message)
        return formatted_message

    def find_query(self, query): #Checks each word in the message for a matching emoji
        emoji_set = set(self.custom_emoji_list.keys())
        if query.startswith(':') and query.endswith(':'):
            return query[1:-1]
        elif random.random() <= 1.0:
            if query in emoji_set:
                for emote in difflib.get_close_matches(query, self.custom_emoji_list, 3, .85):
                       return emote
            for emoji in self.emoji_dict:
                if query in self.emoji_dict[emoji]['list']:
                    return emoji

    def get_fields(self, output_list): #Gets fields for reaction adding
        for output in output_list:
            try:
                for users in self.users_list: 
                    if output['user'] == users['id']:
                        name = users['name']
                return output['text'], output['channel'], output['ts'], output['user'], name
            except:
                print("Failed to parse")
                return None, None, None, None, None

    def parse_message(self, slack_message): #Parses each message sent
        text, channel, timestamp, user, username = self.get_fields(slack_message)
        if text and channel and timestamp and user:
            text = self.format_text(text)
            emoji_list = self.search_list(text.split())
            return emoji_list, channel, timestamp, user, username
        else:
            return None, None, None, None, None
