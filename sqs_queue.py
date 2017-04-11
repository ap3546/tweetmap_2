import boto.sqs
from boto.sqs.message import Message

class queue:

	def __init__(self):

		conn = boto.sqs.connect_to_region(
			'us-east-1',
			aws_access_key_id='aws_access_key_id',
			aws_secret_access_key='aws_secret_access_key')

		# checks if SQS queue exists and creates a queue if it doesn't exist
		self.q = conn.create_queue('twitt_queue')

	# sends a message to the SQS queue
	def send_message(self, message_contents):
		try:
			message = Message()
			message.set_body(message_contents)
			self.q.write(message)
		except:
			print 'Message could not be written to queue'

	# grabs a message from the queue and pops it
	def get_message(self):
		message = self.q.read()
		message_contents = message.get_body() if message else None
		# we need to pop the message from sqs
		if message:
			self.q.delete_message(message)
		return message_contents

	# gets the number of messages currently in the queue
	def count(self):
		return self.q.count()