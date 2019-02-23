import json


class EmojiParser:

    def __init__(self, slack_client):
        # grabs the custom emoji list for server
        self.custom_emoji_list = slack_client.api_call("emoji.list")["emoji"]
        self.users_list = slack_client.api_call("users.list")["members"]
        # load emojis file
        with open('emoji.json') as data_file:
            self.data = json.load(data_file)

    def search_list(self, query_list):
        result_set = list()
        for query in query_list:
            if query in self.custom_emoji_list:
                result_set.append(query)
            result_set.append(self.find_query(query))
        return result_set

    def format_text(self, message):
        formatted_message = message.lower()
        return formatted_message

    def find_query(self, query):
        emoji = self.data["emoji"]
        for sub_list in emoji:
            if query == sub_list[0]:
                return query
            elif query == 'ok':
                return 'ohkay'
            elif query == 'f':
                return 'letter_f'
            elif query in ['ty', 'thanks', 'thx', 'thank']:
                return 'np'
            elif query in ['peach', 'ass']:
                return 'peach'

    # temporary function
    def get_fields(self, output_list):
        for output in output_list:
            if 'subtype' in output:
                if output['subtype'] == 'slackbot_response':
                    return output['text'], output['channel'], output['ts'], output['user'], 'Slackbot'
                else:    
                    return output['text'], output['channel'], output['ts'], output['bot_id'], 'Some Bot'
            else:
                for users in self.users_list: 
                    if output['user'] == users['id']:
                        name = users['name']
                return output['text'], output['channel'], output['ts'], output['user'], name
    BOT_ID = 'UGDKW5T8F'

    def parse_message(self, slack_message):
        text, channel, timestamp, user, username = self.get_fields(slack_message)
        text = self.format_text(text)
        if text and channel and timestamp and user != self.BOT_ID:
            emoji_list = self.search_list(text.split())
            return emoji_list, channel, timestamp, user, username
