from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Request
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# for oauth
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/calendar']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'

# for "InsecureTransportError ("OAuth 2 MUST utilize https")"
# (https://stackoverflow.com/questions/27785375/testing-flask-oauthlib-locally-without-https/27785830)
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'



# Create your views here.

def register(request):
    if request.method == "POST":
        username =  request.POST['username']
        password = request.POST['password']
        try:
            User.objects.create_user(username, '', password)
            return redirect('signin')
        except IntegrityError:
            return render(request, 'calendarapp/register.html', {
                'error': 'このユーザーは既に登録されています'
            })
    return render(request, 'calendarapp/register.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            return redirect('signin')
    return render(request, 'calendarapp/signin.html')


# @login_required
def main(request):
    if request.method == 'POST':
        pass
    else:
        if 'credentials' not in request.session:
            return redirect('authorize')

        # below is in case utilizing json-type-credentials by storing credentials in database
        # credentials = google.oauth2.credentials.Credentials(request.session['credentials'])

        credentials_dict = request.session['credentials']
        credentials = google.oauth2.credentials.Credentials(
            token = credentials_dict["token"],
            refresh_token = credentials_dict["refresh_token"],
            token_uri = credentials_dict["token_uri"],
            client_id = credentials_dict["client_id"],
            client_secret = credentials_dict["client_secret"],
            scopes = credentials_dict["scopes"])

        # build service and execute
        service = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=credentials)

        page_token = None
        while True:
            events = service.events().list(calendarId='primary', pageToken=page_token, timeMin='2021-10-05T00:00:00+09:00', timeMax='2021-11-01T00:00:00+09:00').execute()
            for event in events['items']:
                print(event['summary'])
            page_token = events.get('nextPageToken')
            if not page_token:
                break

        # Save credentials back to session in case access token was refreshed.
        # ACTION ITEM: In a production app, you likely want to save these credentials in a persistent database instead.
        request.session['credentials'] = credentials_to_dict(credentials)

        request.session.clear()

        return render(request, 'calendarapp/main.html')


def authorize(request):
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    # url when authorization done
    flow.redirect_uri = 'http://127.0.0.1:8000/calendar/oauth2callback'

    # authorization-url
    # Enable offline access so that you can refresh an access token without re-prompting the user for permission.
    authorization_url, state = flow.authorization_url(access_type='offline')

    # Store the state so the callback can verify the auth server response.
    request.session['state'] = state

    return redirect(authorization_url)


def oauth2callback(request):
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = request.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = 'http://127.0.0.1:8000/calendar/oauth2callback'

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    request.session['credentials'] = credentials_to_dict(credentials)

    return redirect('main')


@login_required
def request(request):
    pass


def signout(request):
    logout(request)
    return redirect('signin')


def requester_main(request):
    pass

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}
