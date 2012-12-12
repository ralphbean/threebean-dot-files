#!/usr/bin/env python

consumer_token = "a1ecfc33bda40ab34f18c31482011c5e"
consumer_secret = "bbd2653832ba3c3bb2255d78fb6b27c2"

import tweepy

host = 'identi.ca'
api_root = '/api/'
oauth_root = api_root + 'oauth/'

auth = tweepy.OAuthHandler(consumer_token, consumer_secret, 'oob')

auth.OAUTH_HOST = host
auth.OAUTH_ROOT = oauth_root
auth.secure = True

try:
  redirect_url = auth.get_authorization_url()
except tweepy.TweepError:
  print 'Error! Failed to get request token.'
  quit()

print "Go to this URL for verify code: " + redirect_url

req_key = auth.request_token.key
req_secret = auth.request_token.secret

print "enter the verify code from the URL above"
verifier = raw_input('Verify code: ')

auth = tweepy.OAuthHandler(consumer_token, consumer_secret, 'oob')
auth.set_request_token(req_key, req_secret)

auth.OAUTH_HOST = host
auth.OAUTH_ROOT = oauth_root
auth.secure = True

try:
  auth.get_access_token(verifier)
except tweepy.TweepError:
  print 'Error! Failed to get access token.'

print "Store these values in your application. You will re-use them"
print "auth access key is: " + auth.access_token.key
print "auth access secret is: " + auth.access_token.secret
print "done with initialization"
