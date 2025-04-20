from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import json

# Google Drive 權限設定（可根據需要調整）
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def init_google_drive_auth():
    creds = None

    # 如果已經有 token.json，嘗試使用
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # 如果沒有或過期，使用 flow 取得授權
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)  # ✅ 在本地端打開瀏覽器進行授權

        # 儲存 token.json
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds
if __name__ == "__main__":
    creds = init_google_drive_auth()
    print("✅ 已完成授權，token.json 已建立")
