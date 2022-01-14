#!env/bin/python
from time import sleep
from datetime import datetime
from slackclient import SlackClient
from emoji_parser import EmojiParser

# Read in the authentication token
f = open('slacktoken.txt')
key = f.readline().rstrip()
f.close()

def determine_event_type(slack_rtm_output): # Determines which type of event is received
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

if __name__ == "__main__": # Does all the work
    slack_client = SlackClient(key)
    text_parser = EmojiParser(slack_client)
    if slack_client.rtm_connect():
        try:
            print("ReactBot connected and running!")

            while True:
                output_list = slack_client.rtm_read()
                msg_type = determine_event_type(output_list)
                if msg_type == 'text': # Adds emoji to a message based on the parsed output
                    
                    emoji_list, channel, timestamp, user, username, channel_name = text_parser.parse_message(output_list)

                    if emoji_list == None:
                        print("Failed to grab emoji list.\n")
                        continue

                    print(username.encode("utf-8"), "#" + channel_name.encode("utf-8"), [i.encode("utf-8") for i in emoji_list if i not in [None, 'a', 'b', 'o', 'i', 'u', 'thx', 'm', 'v', 'x', 't']])
                    print
                    for emoji_text in emoji_list:
                        if emoji_text not in [None, 'a', 'b', 'o', 'i', 'u', 'm', 'v', 'x', 't']: # Ignore individual letters
                            slack_client.api_call("reactions.add", 
                            channel=channel, 
                            name=emoji_text, 
                            timestamp=timestamp, 
                            as_user=False)

                elif msg_type == 'react': # Adds a react to an existing react 
                    print("+" + output_list[0]['reaction'] + " in #" + text_parser.get_channel(output_list[0]['item']['channel']) + "\n")
                    slack_client.api_call("reactions.add",
                    channel = output_list[0]['item']['channel'],
                    name = output_list[0]['reaction'],
                    timestamp = output_list[0]['item']['ts'],
                    as_user = False)

                elif msg_type == 'invalid': # Ignores everything else
                    output_list = None

                sleep(1.0) # Sleep timer to avoid constant looping


        except: # Shuts down on Ctrl+C in terminal
            print("ReactBot shut down.")

    else:
        print("Connection failed. Invalid Slack token?")
