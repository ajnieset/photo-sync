import json
import logging
from pathlib import Path
from typing import Literal
from webbrowser import open_new

import httpx

PHOTOS_API = "https://photoslibrary.googleapis.com/v1"
CredType = Literal["installed", "web"]
SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly", "https://www.googleapis.com/auth/photoslibrary.appendonly"]
logger = logging.getLogger(__name__)


class PhotosServiceAsync:
    def __init__(self, base_url: str = PHOTOS_API, token: str = str):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

    @staticmethod
    def login(creds_file_path: Path, creds_type: CredType = "installed"):
        with open(creds_file_path, "r") as f:
            creds = json.loads(f.read()).get(creds_type, None)

        if not creds:
            raise Exception
        
        open_new(f"{creds['auth_uri']}?client_id={creds["client_id"]}&redirect_uri={creds["redirect_uris"][0]}&response_type=code&scope={" ".join(SCOPES)}")

    @staticmethod
    def get_token(creds_file_path: Path, access_code: str, creds_type: CredType = "installed"):
        with open(creds_file_path, "r") as f:
            creds = json.loads(f.read()).get(creds_type, None)
        
        if not creds:
            raise Exception
        
        with httpx.Client() as sync_client:
            res = sync_client.post(f"{creds["token_uri"]}", params={
                "code": access_code,
                "client_id": creds["client_id"],
                "client_secret": creds["client_secret"],
                "redirect_uri": creds["redirect_uris"][0],
                "grant_type": "authorization_code",
                "access_type": "offline"
            })
        return res.content

    async def upload_photos(self, photos):
        headers = {
            "Content-type": "application/octect-stream",
            "X-Goog-Upload-Content-Type": "image/jpeg",
            "X-Goog-Upload-Protocol": "raw",
        }
        res = await self.client.post("/upload", data=photos, headers=headers)
        return res.content

    async def create_all(self):
        pass

    async def close(self):
        self.client.aclose()
