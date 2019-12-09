#!env/bin/python
from datetime import datetime
import random
from slackclient import SlackClient
from emoji_parser import EmojiParser
random.seed(datetime.now())

#Read in the authentication token
f = open('slacktoken.txt')
key = f.readline().rstrip()
f.close()

slack_client = SlackClient(key)


def determine_event_type(slack_rtm_output): #Determines which type of event is received
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and 'files' not in output:
                return 'text'
            elif output and 'reaction' in output and output['type'] == 'reaction_added':
                return 'react'
            else:
                return 'invalid'
    return None, None, None, None


if __name__ == "__main__": #Does all the work
    text_parser = EmojiParser(slack_client)
    if slack_client.rtm_connect():
        try:
            print("ReactBot connected and running!")

            # slack_client.api_call("chat.postMessage",
            # channel='#general', 
            # text='ReactBot activated.', 
            # as_user=False, username='MattyBReacts', 
            # icon_url='https://afinde-production.s3.amazonaws.com/uploads/e7133c0d-e92e-46ae-9399-52e9693fa349.jpg')

            while True:
                output_list = slack_client.rtm_read()
                msg_type = determine_event_type(output_list)

                if msg_type == 'text': #Adds emoji to a message based on the parsed output
                    emoji_list, channel, timestamp, user, username = text_parser.parse_message(output_list)

                    if username == "kaitlynohern" and random.random() <= 0.1:
                        #print("Rip Katie", channel, timestamp)
                        slack_client.api_call("chat.delete",
                        channel=channel,
                        ts=timestamp,
                        as_user=True
                        )

                    if emoji_list == None:
                        print("Failed to grab emoji list.")
                        continue

                    print(username, [i for i in emoji_list if i != None])

                    for emoji_text in emoji_list:
                        if emoji_text not in [None, 'a', 'b', 'o', 'i', 'u', 'thx', 'm', 'v', 'x', 't']:
                            slack_client.api_call("reactions.add", 
                            channel=channel, 
                            name=emoji_text, 
                            timestamp=timestamp, 
                            as_user=False)

                elif msg_type == 'react': #Adds a react to an existing react 
                    slack_client.api_call("reactions.add",
                    channel = output_list[0]['item']['channel'],
                    name = output_list[0]['reaction'],
                    timestamp = output_list[0]['item']['ts'],
                    as_user = False)

                elif msg_type == 'invalid': #Ignores everything else
                    output_list = None

        except: #Shuts down on Ctrl+C in terminal
            print("ReactBot shut down.")
            # slack_client.api_call("chat.postMessage",
            # channel='#general', 
            # text='ReactBot deactivated.', 
            # as_user=False, username='MattyBReacts', 
            # icon_url='https://afinde-production.s3.amazonaws.com/uploads/e7133c0d-e92e-46ae-9399-52e9693fa349.jpg')

    else:
        print("Connection failed. Invalid Slack token?")
