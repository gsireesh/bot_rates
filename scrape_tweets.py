import argparse
import json
import twitter

def scrape_twitter(creds, screen_name):
	api = twitter.Api(consumer_key=creds['consumer_key'],
                      consumer_secret=creds['consumer_secret'],
                      access_token_key=creds['access_token_key'],
                      access_token_secret=creds['access_token_secret'])

	tweets = api.GetUserTimeline(screen_name=screen_name, include_rts=False, exclude_replies=True)
	print(len(tweets))
	tweets_dict = [tweet.AsDict() for tweet in tweets]
	return tweets_dict


def store_json(tweets, out_file):
	json.dump(tweets, open(out_file, 'w'))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('config_file', help='Config file for twitter credentials', default='credentials.json')
	args = parser.parse_args()

	creds = json.load(open(args.config_file, 'rb'))
	tweets = scrape_twitter(creds, 'dog_rates')
	store_json(tweets, 'tweets.json')


if __name__ == '__main__':
	main()