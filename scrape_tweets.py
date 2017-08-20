import argparse
import json
import sys
import twitter
import os
from requests import get

# Get a list of tweets from a specified user's timeline
def scrape_twitter_timeline(creds, screen_name):
    api = twitter.Api(consumer_key=creds['consumer_key'],
                      consumer_secret=creds['consumer_secret'],
                      access_token_key=creds['access_token_key'],
                      access_token_secret=creds['access_token_secret'])

    tweets = []
    new_tweets = api.GetUserTimeline(screen_name=screen_name, count=200, include_rts=False, exclude_replies=True, trim_user=True)
    while new_tweets:
        tweets += new_tweets
        oldest_id = tweets[-1].id
        new_tweets = api.GetUserTimeline(screen_name=screen_name, count=200, max_id=oldest_id, include_rts=False, exclude_replies=True, trim_user=True)
        new_tweets = new_tweets[1:]
    return [tweet.AsDict() for tweet in tweets]
    
# filter tweets by whether they have images attached
def filter_valid(tweets):
    valid_tweets = []
    for tweet in tweets:
        if 'media' not in tweet: continue
        media = tweet['media']
        if not any([media_obj['type'] == 'photo' for media_obj in media]): continue
        valid_tweets.append(tweet)
    return valid_tweets

# dump list of dicts into a file
def store_json(tweets, out_file):
    json.dump(tweets, open(out_file, 'w'))

# extract the salient info for tweets: the text and the related image URLS
def filter_text_and_img_urls(tweets):
    text_to_images = {}
    for tweet in tweets:
        text = tweet['text']
        tweet_id = tweet['id']
        urls = []
        media = tweet['media']
        for media_obj in media:
            if not media_obj['type'] == 'photo': continue
            urls.append(media_obj['media_url'])
        text_to_images[text] = urls
    return text_to_images



def download_images(tweets):
    if not os.path.exists('images'):
        os.makedirs('images')
    text_to_filenames = {}
    for (text, urls) in tweets.items():
        file_names = []
        for url in urls:
            file_name = url.split('/')[-1]
            download(url, 'images/' + file_name)
            file_names.append(file_name)
        text_to_filenames[text] = file_names
    return text_to_filenames

def download(url, file_name):
       # open in binary mode
    with open(file_name, "wb") as file:
        # get request
        response = get(url)
        # write to file
        file.write(response.content)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', help='Config file for twitter credentials', default='credentials.json')
    parser.add_argument('existing_tweets', help='file of existing tweets', default='')
    args = parser.parse_args()

    creds = json.load(open(args.config_file, 'rb'))
    if not args.existing_tweets:
        tweets = json.load(open(args.existing_tweets, 'rb'))
    else:
        tweets = scrape_twitter_timeline(creds, 'dog_rates')
        store_json(tweets, 'tweets.json')

    tweets = filter_valid(tweets)
    print ('Working with {} tweets'.format(len(tweets)))

    text_to_images = filter_text_and_img_urls(tweets)
    store_json(text_to_images, 'text_to_urls.json')
    text_to_images = download_images(text_to_images)
    store_json(text_to_images, 'text_to_images.json')
    


if __name__ == '__main__':
    main()