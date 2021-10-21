from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Request, Calendar, Todolist
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
import datetime
import json
from cryptography.fernet import Fernet

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

# user_idを暗号化するためのキー
key = Fernet.generate_key()
f = Fernet(key)



def index(request):
    return render(request, 'calendarapp/index.html')





@login_required
def main(request):
    user = request.user
    if request.method == 'POST':
        id = request.POST['id']
        is_accepted = True if request.POST['is_accepted'] == 'Yes' else False
        message = request.POST['message']

        # カレンダーに予定追加
        if is_accepted:
            event = Request.objects.get(id=id)
            title = event.title
            start = event.start_at.isoformat()[:19]
            end = event.end_at.isoformat()[:19]
            body = {
                'summary': title,
                'start': {
                    'dateTime': start,
                    'timeZone': 'Asia/Tokyo',
                },
                'end': {
                    'dateTime': end,
                    'timeZone': 'Asia/Tokyo',
                },
            }
            credentials_dict = json.loads(Calendar.objects.get(user=user).credentials)
            credentials = get_credentials(credentials_dict)
            service = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
            service.events().insert(calendarId='primary', body=body).execute()

        # リクエストテーブル更新
        Request.objects.filter(id=id).update(admin_message=message, is_accepted=is_accepted)

        # メール送信
        sender_name = user.username
        mail_address = Request.objects.get(id=id).requester_mail_address
        email(sender_name, message, mail_address, is_accepted)

        return redirect('main')
    else:
        # 現在日時と30日後の日時をISOフォーマットで取得
        dt_now_iso, dt_30d_later_iso = get_datetime()

        # Googleカレンダーから予定を取ってくる
        credentials_dict = json.loads(Calendar.objects.get(user=user).credentials)
        event_list = build_service_get_event_list(credentials_dict, dt_now_iso, dt_30d_later_iso)

        # リクエスト一覧をデータベースから取得
        requests = Request.objects.filter(user=user, is_accepted=None)

        # requestsからフロントに送る情報をrequest_listに抽出、datetimeをISOに整形 (id, requester_name, message, start, end)
        request_list = list()
        for a_request in requests:
            dt_request = a_request.end_at
            dt_now = datetime.datetime.now(datetime.timezone.utc)
            if dt_request < dt_now:
                Request.objects.filter(user=user, pk=a_request.pk).delete()
            request_info = dict()
            request_info['id'] = a_request.id
            request_info['requester_name'] = a_request.requester_name
            request_info['title'] = a_request.title
            request_info['start'] = a_request.start_at.isoformat()[:19]
            request_info['end'] = a_request.end_at.isoformat()[:19]
            request_info['message'] = a_request.message
            request_list.append(request_info)

        # URL共有用にuser_idを暗号化
        target = str(user.id).encode()
        crypted_id = f.encrypt(target).decode()  # URLに含めるためにstringに変換

        # UPDATE database?
        # Save credentials back to session in case access token was refreshed.
        # request.session['credentials'] = credentials_to_dict(credentials)

        return render(request, 'calendarapp/main.html', {
            'event_list': event_list,
            'request_list': request_list,
            'crypted_id': crypted_id,
        })


@login_required
def request(request):
    user = request.user
    requests = Request.objects.filter(user=user, is_accepted=None)
    request_list = list()
    for a_request in requests:
        request_info = dict()
        request_info['requester_name'] = a_request.requester_name
        request_info['title'] = a_request.title
        request_info['start'] = a_request.start_at.strftime('%m月%d日%H:%M')
        request_info['end'] = a_request.end_at.strftime('%m月%d日%H:%M')
        request_info['message'] = a_request.message
        request_info['created_at'] = a_request.created_at.strftime('%m月%d日%H:%M')
        request_list.append(request_info)
    return render(request, 'calendarapp/request.html', {
        'request_list': request_list
    })


def logout(request):
    logout(request)
    return redirect('login')

@login_required
def todolist(request):
    user = request.user
    if request.method =='POST':
        title = request.POST['title']
        url = request.POST['url']
        Todolist.objects.create(user=user, title=title, url=url)
        return redirect('todolist')
    else:
        todo_list = Todolist.objects.filter(user=user)
        return render(request, 'calendarapp/todolist.html', {
            'todo_list': todo_list
        })



@login_required
def delete(request, pk):
    user = request.user
    Todolist.objects.filter(user=user, pk=pk).delete()
    return redirect('todolist')





def requester_main(request, crypted_id):
    user_id = f.decrypt(crypted_id.encode()).decode()
    user = get_user_model().objects.get(pk=user_id)
    if request.method == 'POST':
        # DBへ保存
        requester_name = request.POST['requester_name']
        requester_mail_address = request.POST['requester_mail_address']
        title = request.POST['title']
        start_at = request.POST['start_at']
        end_at = request.POST['end_at']
        message = request.POST['message']
        Request.objects.create(user=user, requester_name=requester_name, requester_mail_address=requester_mail_address, title=title,
                                message=message, start_at=start_at, end_at=end_at)

        # メール送信
        mail_address = 'croissant.calendar@gmail.com'  # user.email
        email(requester_name, message, mail_address)

        # request.session.clear()

        return redirect('requester_main', crypted_id=crypted_id)
    else:
        request.session['crypted_id'] = crypted_id  # requesterがGoogleカレンダーと連携した後のコールバックで使う

        # 時間取得
        dt_now_iso, dt_30d_later_iso = get_datetime()

        # 以下でadminの予定を取ってくる
        credentials_dict = json.loads(Calendar.objects.get(user=user).credentials)
        event_list = build_service_get_event_list(credentials_dict, dt_now_iso, dt_30d_later_iso)
        requester_event_list = list()

        for event in event_list:
            if event['calendar_id'] != 'ja.japanese#holiday@group.v.calendar.google.com':
                event['title'] = '予定あり'

        # requesterがGoogleカレンダーと連携していれば、予定を取ってくる
        if 'credentials' in request.session:
            requester_credentials_dict = request.session['credentials']
            requester_event_list = build_service_get_event_list(requester_credentials_dict, dt_now_iso, dt_30d_later_iso)

        # やりたいことリスト
        todo_list = list(Todolist.objects.filter(user=user).values())

        return render(request, 'calendarapp/requester_main.html', {
            'event_list': event_list,
            'requester_event_list': requester_event_list,
            'todo_list': todo_list
        })


def email(sender_name, message, mail_address, *is_accepted):
    # admin or actor によってtitle, contentを変える(is_acceptedの有無で条件分岐):
    if is_accepted:  # from admin to actor
        result = '承認' if is_accepted[0] == True else '拒否'
        title = sender_name + 'さんへのリクエストが' + result + 'されました'
        content = sender_name + 'さんへのリクエストが' + result + 'されました。\n\n' + sender_name + 'さんからのメッセージ：' + message
    else:  # from actor to admin
        title = sender_name + 'さんからasobo!のリクエストが送られてきました'
        content = sender_name + 'さんからリクエストが来ています。\n\n確認する：http://127.0.0.1:8000/accounts/login/'
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


def get_credentials(credentials_dict):
    return google.oauth2.credentials.Credentials(
        token=credentials_dict["token"],
        refresh_token=credentials_dict["refresh_token"],
        token_uri=credentials_dict["token_uri"],
        client_id=credentials_dict["client_id"],
        client_secret=credentials_dict["client_secret"],
        scopes=credentials_dict["scopes"])


def get_datetime():
    dt_now = datetime.datetime.now()
    dt_now_iso = dt_now.isoformat()[:19] + 'Z'
    dt_30d_later_iso = (dt_now + datetime.timedelta(days=30)).isoformat()[:19] + 'Z'
    return (dt_now_iso, dt_30d_later_iso)


# カレンダーのリスト取得
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


# calendar_id_listに追加したそれぞれのカレンダーからイベントを取得
# イベントの「タイトル(title)、開始日時(start)、終了日時(end)」の情報を辞書形式で持ったevent_infoを作成し、それをevent_listに追加
def get_event_list(calendar_id_list, service, dt_now_iso, dt_30d_later_iso):
    event_list = list()
    for calendar_id in calendar_id_list:
        page_token = None
        while True:
            events = service.events().list(calendarId=calendar_id, pageToken=page_token, timeMin=dt_now_iso, timeMax=dt_30d_later_iso).execute()
            for event in events['items']:
                event_info = dict()
                event_info['calendar_id'] = calendar_id
                event_info['title'] = event['summary']
                if 'dateTime' in event['start']:  # ISO表記
                    event_info['start'] = event['start']['dateTime'][:19]  # 秒以下を取り除く
                    event_info['end'] = event['end']['dateTime'][:19]
                elif 'date' in event['start']:  # all-dayのイベント、ハイフンでつないだ表記
                    event_info['start'] = event['start']['date']
                    event_info['end'] = event['end']['date']
                event_list.append(event_info)
            page_token = events.get('nextPageToken')
            if not page_token:
                break

    return event_list


def build_service_get_event_list(credentials_dict, dt_now_iso, dt_30d_later_iso):
    credentials = get_credentials(credentials_dict)
    service = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials) # build service
    calendar_id_list = get_calendar_id_list(service)
    event_list = get_event_list(calendar_id_list,service, dt_now_iso, dt_30d_later_iso)
    return event_list


def authorize_requester(request):
    request.session['temp'] = 'temp'
    return redirect('authorize')


def authorize(request):
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    # url when authorization done
    flow.redirect_uri = 'http://127.0.0.1:8000/oauth2callback'

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
    flow.redirect_uri = 'http://127.0.0.1:8000/oauth2callback'

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    credentials = credentials_to_dict(credentials)
    if 'temp' in request.session:  # Store credentials in the session.
        request.session['credentials'] = credentials
        return redirect('requester_main', crypted_id=request.session['crypted_id'])
    else:  # Store credentials in the database.
        credentials = json.dumps(credentials)
        user = request.user
        Calendar.objects.create(user=user, credentials=credentials)
        return redirect('main')
