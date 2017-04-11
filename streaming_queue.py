import random
import time

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from sqs_queue import queue

import json

# Variables that contains the user credentials to access Twitter API
access_token = 'access_token'
access_token_secret = 'access_token_secret'
consumer_key = 'consumer_key'
consumer_secret = 'consumer_secret'

kws = ["Trump", "ethereum", "bitcoin", "factom", "litecoin", "monero", "ripple", "zcash", "golem", "the"]

q = queue()

class MyStreamListener(StreamListener):
    def on_data(self, data):
        if data:
            tweet = json.loads(data)
            try:
                if 'geo' in tweet and tweet['geo']:
                    for key in kws:
                        if key.lower() in tweet['text'].lower(): # not case-sensitive
                            tweet_data = {'keyword': key.lower()}
                            if 'coordinates' in tweet and tweet['coordinates']:
                                tweet_data['coordinates'] = tweet['coordinates']['coordinates']
                            else:
                                tweet_data['coordinates'] = None
                            if 'text' in tweet and tweet['text']:
                                tweet_data['text'] = tweet['text']
                            else:
                                tweet_data['text'] = None
                            if 'created_at' in tweet and tweet['created_at']:
                                tweet_data['timestamp'] = tweet['created_at']
                            else:
                                tweet_data['timestamp'] = None
                            if 'user' in tweet and tweet['user']:
                                tweet_data['author'] = tweet['user']['name']
                            else:
                                tweet_data['author'] = None

                            print tweet
                            q.send_message(json.dumps(tweet_data))
                            print q.count()
                    return True

            except Exception as e:
                print("Error: " + str(e))
                return True
        return True

    def on_error(self, status_code):
        if status_code == 420:
            print "Error: Too many calls... need to sleep..."
            nsecs = random.randint(80, 100)
            time.sleep(nsecs)
        else:
            print "Err: " + str(status_code)
        return True

if __name__ == '__main__':
    listener = MyStreamListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, listener)
    stream.filter(track=kws, locations=[-180, -90, 180, 90])
