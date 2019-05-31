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
        elif random.random() < 0.25:
            if query in emoji_set:
                for emote in difflib.get_close_matches(query, self.custom_emoji_list, 3, .85):
                       return emote
            elif query == 'ok':
                return 'ohkay'
            elif query in ['ty', 'thanks', 'thx', 'thank']:
                return 'np'
            elif query in ['peach', 'ass', 'booty', 'butt']:
                return 'peach'
            elif query in ['cock', 'dick', 'penis', 'dong']:
                return 'eggplant'
            elif query  in ['angry', '&gt;:(', 'd:&lt;', '):&lt;']:
                return 'angryface'
            elif query in ['hankey', 'poop', 'turd', 'shit', 'crap', 'feces', 'dookie', 'poopy', 'poopie', 'shid', 'shidded']:
                return 'poop'
            elif query in ['hehe', 'heehee']:
                return 'xd'
            elif query == 'corn':
                return 'corn1'

    # Ignore the shitty hardcoding
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
            # if 'subtype' in output and 'attachments' not in output:
            #     if output['subtype'] in ['slackbot_response', 'channel_topic', 'me_message']:
            #         return output['text'], output['channel'], output['ts'], output['user'], 'Event'
            #     else:    
            #         return output['text'], output['channel'], output['ts'], output['bot_id'], 'Some Bot'
            # elif 'attachments' in output:
            #     if output['username'] == 'Polly':
            #         return 'Polly', output['channel'], output['ts'], output['bot_id'], 'Polly'
            #     else:
            #         print(output['attachments']['text'], output['channel'], output['ts'], output['user'], 'Quoted Message')
            #         return 'Quoted Message', output['channel'], output['ts'], output['user'], 'Quoted Message'
            # else:
            #     for users in self.users_list: 
            #         if output['user'] == users['id']:
            #             name = users['name']
            #     return output['text'], output['channel'], output['ts'], output['user'], name

    def parse_message(self, slack_message): #Parses each message sent
        text, channel, timestamp, user, username = self.get_fields(slack_message)
        if text and channel and timestamp and user:
            text = self.format_text(text)
            emoji_list = self.search_list(text.split())
            return emoji_list, channel, timestamp, user, username
        else:
            return None, None, None, None, None
