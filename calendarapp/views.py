from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Request, Calendar
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

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

import datetime
import json



# Create your views here.

def index(request):
    return render(request, 'calendarapp/index.html')


def register(request):
    if request.method == "POST":
        username =  request.POST['username']
        password = request.POST['password']
        try:
            User.objects.create_user(username, '', password)
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('authorize')
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


@login_required
def main(request):
    user = request.user
    if request.method == 'POST':
        # フロントでの処理がどうなっているのかやまとさんに確認
        # リクエストのIDをフロントから送ってもらう？
        # is_accepted = request.POST['is_accepted'] みたいなので受け取る？
        # message = request.POST['message']
        # if 承認:
            # カレンダーに予定追加

        # データベース更新（Request.message, Request.is_accepted）

        # メール送信
        # sender_name = user.username
        # mail_address = # リクエストのIDから取ってくる？
        # email(sender_name, message, mail_address, is_accepted)
        # return redirect('main')
        pass
    else:
        credentials_dict = json.loads(Calendar.objects.get(user=user).credentials)
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

        # カレンダーのリスト取得
        calendar_id_list = get_calendar_id_list(service)

        # 現在日時と1年後の日時をISOフォーマットで取得
        dt_now_iso, dt_90d_later_iso = get_datetime()

        # calendar_id_listに追加したそれぞれのカレンダーからイベントを取得
        event_list = get_event_list(calendar_id_list, service, dt_now_iso, dt_90d_later_iso)

        # リクエスト一覧をデータベースからとって表示
        requests = Request.objects.filter(user=user, is_accepted=None)
        # 辞書のリストに変換
        requests = list(requests.values())

        # UPDATE database?
        # Save credentials back to session in case access token was refreshed.
        # request.session['credentials'] = credentials_to_dict(credentials)

        return render(request, 'calendarapp/main.html', {
            'event_list': event_list,
            'requests': requests,
            'user_id': user.id,  # URL共有用
        })


@login_required
def request(request):
    user = request.user
    requests = Request.objects.filter(user=user, is_accepted=None)
    return render(request, 'calendarapp/request.html', {
        'requests': requests
    })


def signout(request):
    logout(request)
    return redirect('signin')


def requester_main(request):
    user_id = 13 # need to get from URL-info
    user = User.objects.get(pk=user_id)
    if request.method == 'POST':
        # DBへ保存
        requester_name = request.POST['requester_name']
        requester_mail_address = request.POST['requester_mail_address']
        message = request.POST['message']
        start_at = request.POST['start_at']
        end_at = request.POST['end_at']
        Request.objects.create(user=user, requester_name=requester_name,requester_mail_address=requester_mail_address, message=message, start_at=start_at, end_at=end_at)

        # メール送信
        mail_address = 'croissant.calendar@gmail.com'  # user.email
        email(requester_name, message, mail_address)

        return redirect('requester_main')

    else:
        credentials_dict = json.loads(Calendar.objects.get(user=user).credentials)
        credentials = google.oauth2.credentials.Credentials(
            token = credentials_dict["token"],
            refresh_token = credentials_dict["refresh_token"],
            token_uri = credentials_dict["token_uri"],
            client_id = credentials_dict["client_id"],
            client_secret = credentials_dict["client_secret"],
            scopes = credentials_dict["scopes"])

        service = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=credentials)

        calendar_id_list = get_calendar_id_list(service)

        dt_now_iso, dt_90d_later_iso = get_datetime()

        event_list = get_event_list(calendar_id_list, service, dt_now_iso, dt_90d_later_iso)

        return render(request, 'calendarapp/requester_main.html', {
            'event_list': event_list,
        })


def email(sender_name, message, mail_address, *is_accepted):
    # admin or actor によってtitle, contentを変える(is_acceptedの有無で条件分岐):
    if is_accepted: # from admin to actor
        title = 'from admin to actor'
        content = 'test'
    else:           # from actor to admin
        title = 'from actor to admin'
        content = 'test'
    send_mail(
        title,
        content,
        'croissant.calendar@gmial.com',
        [mail_address],
        fail_silently=False,
    )


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def get_datetime():
    dt_now = datetime.datetime.now()
    dt_now_iso = dt_now.isoformat()[:19] + 'Z'
    dt_90d_later_iso = (dt_now + datetime.timedelta(days=90)).isoformat()[:19] + 'Z'
    return (dt_now_iso, dt_90d_later_iso)


def get_calendar_id_list(service):
    calendar_id_list = list()
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            calendar_id_list.append(calendar_list_entry['id'])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    return calendar_id_list


# イベントの「タイトル(title)、開始日時(start)、終了日時(end)」の情報を辞書形式で持ったevent_infoを作成し、それをevent_listに追加
def get_event_list(calendar_id_list, service, dt_now_iso, dt_90d_later_iso):
    event_list = list()
    for calendar_id in calendar_id_list:
        page_token = None
        while True:
            events = service.events().list(calendarId=calendar_id, pageToken=page_token, timeMin=dt_now_iso, timeMax=dt_90d_later_iso).execute()
            for event in events['items']:
                event_info = dict()
                event_info['title'] = event['summary']
                if 'dateTime' in event['start']: # ISO表記
                    event_info['start'] = event['start']['dateTime'][:19] # 秒以下を取り除く
                    event_info['end'] = event['end']['dateTime'][:19]
                elif 'date' in event['start']:   # all-dayのイベント、ハイフンでつないだ表記
                    event_info['start'] = event['start']['date']
                    event_info['end'] = event['end']['date']
                event_list.append(event_info)
            page_token = events.get('nextPageToken')
            if not page_token:
                break

    return event_list


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
    user = request.user
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = request.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = 'http://127.0.0.1:8000/calendar/oauth2callback'

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the database.
    credentials = flow.credentials
    credentials = json.dumps(credentials_to_dict(credentials))
    Calendar.objects.create(user=user, credentials=credentials)

    return redirect('main')
