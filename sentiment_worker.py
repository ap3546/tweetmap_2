from streaming_queue import q
import boto.sns
import thread
import requests, json
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from time import sleep
import watson_developer_cloud.natural_language_understanding.features.v1 as features

nlp = NaturalLanguageUnderstandingV1(
    username = 'username',
    password = 'password',
    version = '2017-02-27')

class notification():

	def __init__(self):

		self.conn = boto.sns.connect_to_region(
			'us-west-2',
			aws_access_key_id='aws_access_key_id',
			aws_secret_access_key='aws_secret_access_key')
		self.arn = 'arn:aws:sns:us-west-2:441490072748:twitt_map'

	def publish(self, message):

		response = self.conn.publish(self.arn, message, subject='Tweet')
		print response

def get_sentiment(content):
	try:
		resp = nlp.analyze(text=content, features=[features.Sentiment()])
		response = resp["sentiment"]["document"]["score"]
		print str(response) + ": " + content
		return response
	except:
		print "Error getting sentiment from Watson NLU"
		return None

def worker_thread(tweet, n):

	tweet = json.loads(tweet)
	text = tweet['text']
	sentiment = get_sentiment(text)
	# only publish tweet to SNS if there is actually a sentiment returned from Watson
	if sentiment:
		tweet['sentiment'] = sentiment
		n.publish(json.dumps(tweet))
		print json.dumps(tweet)

if __name__ == '__main__':

	n = notification()
	while True:
		tweet = q.get_message()
		if tweet:
			thread.start_new_thread(worker_thread, (tweet, n,))
		sleep(10)
