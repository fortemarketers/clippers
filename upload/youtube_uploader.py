import os
import json
import pickle
import logging
import tempfile
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_service(channel_id: str, credentials_file: str, token_file: str):
    creds = None

    # Try loading token from environment variable first
    token_env = os.getenv(f"{channel_id.upper()}_TOKEN")
    if token_env:
        try:
            creds = pickle.loads(bytes.fromhex(token_env))
        except Exception:
            pass

    # Try loading from file
    if not creds and os.path.exists(token_file):
        with open(token_file, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Load client secrets from env variable or file
            secrets_env = os.getenv(f"{channel_id.upper()}_CLIENT_SECRETS")
            if secrets_env:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                                  delete=False) as tmp:
                    tmp.write(secrets_env)
                    tmp_path = tmp.name
            else:
                tmp_path = credentials_file

            flow = InstalledAppFlow.from_client_secrets_file(tmp_path, SCOPES)
            creds = flow.run_local_server(port=0)

            if secrets_env:
                os.unlink(tmp_path)

        # Save token
        with open(token_file, "wb") as f:
            pickle.dump(creds, f)

        # Save token to env-friendly hex for cloud
        token_hex = pickle.dumps(creds).hex()
        logger.info(f"TOKEN_HEX for {channel_id}: {token_hex[:50]}...")

    return build("youtube", "v3", credentials=creds)


def upload_video(video_path: str, thumb_path: str, title: str,
                 description: str, tags: list,
                 credentials_file: str, token_file: str,
                 channel_id: str = "ch1") -> str:
    yt = get_service(channel_id, credentials_file, token_file)
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:30],
            "categoryId": "27",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        }
    }
    media = MediaFileUpload(video_path, mimetype="video/mp4",
                            resumable=True, chunksize=5*1024*1024)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = req.next_chunk()
    video_id = response["id"]
    logger.info(f"Uploaded: https://youtube.com/shorts/{video_id}")

    if thumb_path and os.path.exists(thumb_path):
        try:
            yt.thumbnails().set(videoId=video_id,
                                media_body=MediaFileUpload(thumb_path)).execute()
        except Exception as e:
            logger.warning(f"Thumb upload failed: {e}")
    return video_id
