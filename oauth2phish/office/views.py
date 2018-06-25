from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
#from office.authhelper import get_signin_url, get_token_from_code, get_access_token
#from office.outlookservice import get_me, get_my_messages, get_my_events
from .models import DBwrapper, Auth, O2mail
import time
import requests





def home(request):
    DBwrapper.DBwrapper()
    accs =  DBwrapper.getOfficeAcc()

    for elm in accs:
        print(elm[1])
    context = {
        'accs':accs,
    }
    return render(request, 'office/home.html', context)


def link(request):
    redirect_uri = request.build_absolute_uri(reverse('office:gettoken'))
    sign_in_url = Auth.get_signin_url(redirect_uri)
    return HttpResponse('<a href="' + sign_in_url +'">Click here to sign in and view your mail</a>')


def mail(request):
    try:
        request.session["user_id"] = request.GET["user_id"]
        access_token = Auth.get_access_token(request, request.build_absolute_uri(reverse('office:gettoken')))
        messages = O2mail.get_my_messages(access_token)
    except:
        return render(request, 'office/mail.html')
    access_token = DBwrapper.getAccessToken(user_id)
#    mails =  DBwrapper.getMailsFromOfficeAcc(user_id)
    context = {
        'mails':mails,
    }
    return render(request, 'office/mail.html', context)

def gettoken(request):
    auth_code = request.GET['code']
    session_state = request.GET['session_state']

    redirect_uri = request.build_absolute_uri(reverse('office:gettoken'))
    token = Auth.get_token_from_code(auth_code, redirect_uri)
    access_token = token['access_token']
    user = O2mail.get_me(access_token)
    refresh_token = token['refresh_token']
    expires_in = token['expires_in']


    # expires_in is in seconds
    # Get current timestamp (seconds since Unix Epoch) and
    # add expires_in to get expiration time
    # Subtract 5 minutes to allow for clock differences
    expiration = int(time.time()) + expires_in - 300

    # Save the token in the session
    request.session['access_token'] = access_token
    request.session['refresh_token'] = refresh_token
    request.session['token_expires'] = expiration


    ###################################################################
    DBwrapper.addTokenToOffice(user['displayName'], user['mail'], token, access_token, refresh_token, expiration, session_state)
    ###################################################################

    return HttpResponseRedirect(reverse('office:home'))


def events(request):
    access_token = Auth.get_access_token(request, request.build_absolute_uri(reverse('office:gettoken')))
    # If there is no token in the session, redirect to home
    if not access_token:
        return HttpResponseRedirect(reverse('office:home'))
    else:
        events = O2mail.get_my_events(access_token)
        context = { 'events': events['value'] }
        return render(request, 'office/events.html', context)