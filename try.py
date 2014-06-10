# Fill in your app parameters here.
FITBIT_APP_KEY = 'ebbd6f22f4444e67817db51c7ff8c100'
FITBIT_APP_SECRET = '516cb73b15624dd4a4f64d925f918c74'

import oauth2
consumer = oauth2.Consumer(key=FITBIT_APP_KEY, secret=FITBIT_APP_SECRET)
client = oauth2.Client(consumer)
resp, content = client.request('http://api.fitbit.com/oauth/request_token', 'GET')
print resp
print content
token = oauth2.Token.from_string(content)
# NOTE: the auth URL uses www.fitbit.com as the domain, NOT api.fitbit.com
auth_url = 'http://www.fitbit.com/oauth/authorize?oauth_token={0}'.format(token.key)
print auth_url