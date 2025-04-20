from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import re
from api.utils import constants

class GoogleDriveClient:
    def __init__(self):
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        token_path = 'token.json'
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, constants.SCOPES)
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', constants.SCOPES)
            auth_url, _ = flow.authorization_url(prompt='consent')

            print("請開啟以下網址完成授權流程：\n", auth_url)
            code = input("輸入授權碼：")
            flow.fetch_token(code=code)
            creds = flow.credentials
        return build('drive', 'v3', credentials=creds)

    def _extract_folder_id(self, url: str) -> str:
        match = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)
        if not match:
            raise ValueError(f"無法從網址解析資料夾 ID：{url}")
        return match.group(1)

    def _list_all_files_recursive(self, folder_id: str, collected=None):
        if collected is None:
            collected = []

        query = f"'{folder_id}' in parents and trashed = false"
        results = self.service.files().list(
            q=query,
            pageSize=1000,
            fields="files(id, name, mimeType, webViewLink)"
        ).execute()

        for item in results.get('files', []):
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                self._list_all_files_recursive(item['id'], collected)
            else:
                collected.append({
                    'name': item['name'],
                    'url': item['webViewLink']
                })

        return collected

    def get_all_files(self, folder_urls: list[str]) -> list[dict]:
        all_files = []
        for url in folder_urls:
            folder_id = self._extract_folder_id(url)
            files = self._list_all_files_recursive(folder_id)
            all_files.extend(files)
        return all_files
