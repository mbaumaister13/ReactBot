import json
from nis import cat
import string
import difflib
import random
from datetime import datetime
random.seed(datetime.now())

class EmojiParser:
    def __init__(self, slack_client):
        # Grabs the custom emoji list, user list and emoji dictionary for server
        self.custom_emoji_list = slack_client.api_call("emoji.list")["emoji"]
        self.users_list = slack_client.api_call("users.list")["members"]
        self.channel_list = slack_client.api_call("conversations.list")["channels"]
        self.emoji_set = set(self.custom_emoji_list.keys())
        with open("emoji_dict.txt") as json_file:
            self.emoji_dict = json.load(json_file)

    def get_channel(self, channel_id):
        for channel in self.channel_list:
            if channel_id == channel['id'] and channel['is_channel']:
                return channel['name']
        return "private channel or dm"

    def get_user(self, user_id):
        for users in self.users_list:
            if(user_id == users['id']):
                return users['name']
        return None

    def get_random_emote(self):
        return random.choice([emote for emote in list(self.custom_emoji_list.keys()) if not any(x in emote for x in ['bighdm', 'mf', 'gopher'])])

    def search_message(self, query_list): # Adds found emoji matches to the result set
        result_set = set()
        for query in query_list:
            for emote in self.find_emotes(query):
                result_set.add(emote)
        return result_set

    def format_message(self, message): # Lowercases the message and removes certain punctuation
        formatted_message = message.lower()
        for char in string.punctuation:
            if char not in ['_', ':', '(', ')', '&', ';', '-']:
                formatted_message = formatted_message.replace(char, ' ')
        print(formatted_message)
        return formatted_message

    def find_emotes(self, query): # Checks each word in the message for a matching emoji
        try:
            emotes = set()
            if query.startswith(':') and query.endswith(':'):
                emotes.add(query[1:-1])

            if random.random() <= .33: # Adjust this value between 0-1 to change random chance of react.
                if query.startswith('j'):
                    emotes.add('j')
                
                matching_queries = difflib.get_close_matches(query, self.emoji_set, 100, .5) # Adjust decimal value to determine partial match strength
                
                matching_emote_set = set()
                for match in matching_queries:
                    matching_emote_set.add(match)

                if len(matching_emote_set) > 0:
                    matching_emote_list = list(matching_emote_set)
                    random_number = random.randint(1, 3)
                    num = 0
                    while num < random_number:
                        emote = matching_emote_list[random.randint(0, len(matching_emote_list)-1)]
                        if emote not in emotes:
                            emotes.add(emote)
                            num += 1
                            
                            

                for emoji in self.emoji_dict:
                    if query in self.emoji_dict[emoji]['list']:
                        emotes.add(emoji)
            return emotes
        except Exception as e:
            print(e)

    def get_message_fields(self, output_list): # Gets fields for reaction adding
        for output in output_list:
            try:
                return output['text'], output['channel'], output['ts'], output['user'], self.get_user(output['user']), self.get_channel(output['channel'])
            except:
                print("Failed to parse")
                return None, None, None, None, None, None


    def parse_message(self, slack_message): # Parses each message sent
        text, channel, timestamp, user, username, channel_name = self.get_message_fields(slack_message)
        if text and channel and timestamp and user:
            text = self.format_message(text)
            emoji_list = self.search_message(text.split())
            return emoji_list, channel, timestamp, user, username, channel_name
        else:
            return None, None, None, None, None, None
