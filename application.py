from flask import Flask, request, render_template, Response
import json
import os.path
from time import sleep
import requests
from datetime import datetime
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection

# Note that Amazon EB looks for application.py (not run.py, start.py, etc.)

# Amazon Elastic Beanstalk looks for 'application' object
application = Flask(__name__)

# case of keywords doesn't matter because checked using .lower() -> not case sensitive
kws = ["Trump", "ethereum", "bitcoin", "factom", "litecoin", "monero", "ripple", "zcash", "golem", "the"]

host = 'search-twittmap-fdjmgbx3534p2u3xur3hoaqr44.us-west-2.es.amazonaws.com'
ind = 'twitter'
mapping_type = 'tweet'

AWS_ACCESS_KEY = "AWS_ACCESS_KEY"
AWS_SECRET_KEY = "AWS_SECRET_KEY"
REGION = "us-west-2"

awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, REGION, 'es')

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

file_path = os.path.dirname(__file__)

def convert(original_time):
	timestamp = datetime.strptime(original_time, '%m-%d-%Y %I:%M %p')
	return timestamp.strftime('%a %b %d %H:%M:%S +0000 %Y')

@application.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@application.route('/global', methods=['POST'])
def get_global():
    keyword = request.args['kw'].lower()

    payload = {
        "size": 1000,
        'query': {
            'bool': {
                'must': {
                    'match': {
                        'keyword': keyword
                    }
                }
            }
        },
        "sort": [
            {"timestamp": "asc"}
        ]
    }

    search_res = es.search(index=ind, doc_type=mapping_type, body=payload)
    response = {'tweets': [], 'count': 0, 'pattern': 'global'}
    for hit in search_res['hits']['hits']:
        response['tweets'].append({"text": "@" + hit['_source']['author'] + ": " + hit['_source']['text'],
                                   "sen": hit['_source']['sentiment'],
                                   "coordinates": hit['_source']['coordinates']})
        response['count'] += 1
    return json.dumps(response, indent=3)

@application.route('/sns', methods=['POST'])
def get_sns():
    response = {'new_tweets': 0}
    if 'x-amz-sns-message-type' not in request.headers:
        print "Error"
    content = json.loads(request.get_data())
    # Confirm the subscription
    if request.headers['x-amz-sns-message-type'] == 'SubscriptionConfirmation':
        print content['SubscribeURL']
        # visit the URL to confirm
        r = requests.get(content['SubscribeURL'])
        print r.text
    elif request.headers['x-amz-sns-message-type'] == 'Notification':
        es.index(index=ind, doc_type=mapping_type, body=content['Message'])
        response['new_tweets'] += 1
        # print "XXXX" + str(content['Message'])
    return response

if __name__=='__main__':
    # for testing
    application.run(debug=True)
    # when deployed, Amazon EB by default forwards requests to port 5000
    # application.run(host='0.0.0.0', port=5000)
