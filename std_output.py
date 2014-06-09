#!/usr/bin/env python

'''
Description:
   Using the FitBit API get: http://api.fitbit.com/1/user/-/activities/date/2011-04-17.xml

   Displays:
    <?xml version="1.0" encoding="UTF-8"?><result><summary><activeScore>44</activeScore><caloriesOut>1894</caloriesOut><distances><activityDistance><activity>total</activity><distance>0.11</distance></activityDistance><activityDistance><activity>tracker</activity><distance>0.11</distance></activityDistance><activityDistance><activity>loggedActivities</activity><distance>0</distance></activityDistance><activityDistance><activity>veryActive</activity><distance>0</distance></activityDistance><activityDistance><activity>moderatelyActive</activity><distance>0.03</distance></activityDistance><activityDistance><activity>lightlyActive</activity><distance>0.08</distance></activityDistance><activityDistance><activity>sedentaryActive</activity><distance>0</distance></activityDistance></distances><fairlyActiveMinutes>7</fairlyActiveMinutes><lightlyActiveMinutes>20</lightlyActiveMinutes><sedentaryMinutes>1413</sedentaryMinutes><steps>260</steps><veryActiveMinutes>0</veryActiveMinutes></summary></result>

Reference:
   http://wiki.fitbit.com/display/API/Fitbit+API
   http://wiki.fitbit.com/display/API/API-Get-Activities
   http://wiki.fitbit.com/display/API/OAuth-Authentication-API#OAuth-Authentication-API-TheOAuthFlow
   http://oauth.net/core/1.0a/

Notes: 
   FitBit API rejects oauth.OAuthSignatureMethod_HMAC_SHA1()
   generated signatures so use oauth.OAuthSignatureMethod_PLAINTEXT()
   instead.
'''

#unauth_client = fitbit.Fitbit('ebbd6f22f4444e67817db51c7ff8c100', '516cb73b15624dd4a4f64d925f918c74')

import os, httplib

# Install oauth for python. On Ubuntu run: sudo apt-get install python-oauth
from oauth import oauth

#XXX: register your FitBit client: https://dev.fitbit.com/apps/new
#XXX: which gives you a consumer key/secret
CONSUMER_KEY    = 'd7cfbb894294470ebe090fb083fcb5c1'
CONSUMER_SECRET = 'dc699b301aab4cbaab52422d3c8f8596'

SERVER = 'api.fitbit.com'
REQUEST_TOKEN_URL = 'http://%s/oauth/request_token' % SERVER
ACCESS_TOKEN_URL = 'http://%s/oauth/access_token' % SERVER
AUTHORIZATION_URL = 'http://%s/oauth/authorize' % SERVER

ACCESS_TOKEN_STRING_FNAME = 'access_token.string'
DEBUG = False

# pass oauth request to server (use httplib.connection passed in as param)
# return response as a string
def fetch_response(oauth_request, connection, debug=DEBUG):
   url= oauth_request.to_url()
   connection.request(oauth_request.http_method,url)
   response = connection.getresponse()
   s=response.read()
   if debug:
      print 'requested URL: %s' % url
      print 'server response: %s' % s
   return s

def main():
   connection = httplib.HTTPSConnection(SERVER)
   consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
   # XXX: hmac-sha1 does not work; use plain text
   #signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
   signature_method = oauth.OAuthSignatureMethod_PLAINTEXT()

   # if we don't have a cached access-token stored in a file, then get one
   if not os.path.exists(ACCESS_TOKEN_STRING_FNAME):

      print '* Obtain a request token ...'
      oauth_request = oauth.OAuthRequest.from_consumer_and_token(
            consumer, http_url=REQUEST_TOKEN_URL)
      if DEBUG:
         connection.set_debuglevel(10)
      oauth_request.sign_request(signature_method, consumer, None)
      resp=fetch_response(oauth_request, connection)
      auth_token=oauth.OAuthToken.from_string(resp)
      print 'Auth key: %s' % str(auth_token.key)
      print 'Auth secret: %s' % str(auth_token.secret)
      print '-'*75,'\n\n'

      # authorize the request token
      print '* Authorize the request token ...'
      auth_url="%s?oauth_token=%s" % (AUTHORIZATION_URL, auth_token.key)
      print 'Authorization URL:\n%s' % auth_url
      oauth_verifier = raw_input(
         'Please go to the above URL and authorize the '+
         'app -- Type in the Verification code from the website, when done: ')
      print '* Obtain an access token ...'
      # note that the token we're passing to the new 
      # OAuthRequest is our current request token
      oauth_request = oauth.OAuthRequest.from_consumer_and_token(
         consumer, token=auth_token, http_url=ACCESS_TOKEN_URL,
         parameters={'oauth_verifier': oauth_verifier})
      oauth_request.sign_request(signature_method, consumer, auth_token)

      # now the token we get back is an access token
      # parse the response into an OAuthToken object
      access_token=oauth.OAuthToken.from_string(
         fetch_response(oauth_request,connection))
      print 'Access key: %s' % str(access_token.key)
      print 'Access secret: %s' % str(access_token.secret)
      print '-'*75,'\n\n'


      # write the access token to file; next time we just read it from file
      if DEBUG:
         print 'Writing file', ACCESS_TOKEN_STRING_FNAME
      fobj = open(ACCESS_TOKEN_STRING_FNAME, 'w')
      access_token_string = access_token.to_string()
      fobj.write(access_token_string)
      fobj.close()

   else:
      if DEBUG:
         print 'Reading file', ACCESS_TOKEN_STRING_FNAME
      fobj = open(ACCESS_TOKEN_STRING_FNAME)
      access_token_string = fobj.read()
      fobj.close()

      access_token = oauth.OAuthToken.from_string(access_token_string)

   apiCall = '/1/user/-/activities/date/2011-04-17.xml'
   #apiCall = '/1/user/-/devices.xml'
   #apiCall='/1/user/-/profile.xml'
   #apiCall='/1/user/-/activities/recent.xml'

   # For other FitBit API calls:
   #  http://wiki.fitbit.com/display/API/Resource-Access-API
   #  http://wiki.fitbit.com/display/API/API-Get-Activities

   # access protected resource
   print '* Access a protected resource ...'
   oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer,
      token=access_token, http_url=apiCall)
   oauth_request.sign_request(signature_method, consumer, access_token)
   headers = oauth_request.to_header(realm='api.fitbit.com')
   connection.request('GET', apiCall, headers=headers)
   resp = connection.getresponse()
   xml = resp.read()
   print xml

if __name__ == '__main__':
   main()
