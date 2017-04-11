# TwittMap Assignnment #2

For this assignment, we used Amazon SQS to build a queue of tweets filtered by ten keywords. Then,
workers each operating on unique threads pop messages off of the SQS queue and send them to a Watson
sentiment analysis api (note: at the free tier, daily API calls are limited to 1000). These workers then
send the tweets with sentiment data to SNS with an HTTP endpoint. When notifications are published to that HTTP endpoint,
the correspoding messages are inserted into an Amazon elasticSearch instance that follows the elastic_config.json schema.
From the frontend, one can query by keyword and see visual indications describing the sentiment of the tweets.