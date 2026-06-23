import os
import pickle
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_service(credentials_file: str, token_file: str):
    creds = None
    if os.path.exists(token_file):
        with open(token_file, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "wb") as f:
            pickle.dump(creds, f)
    return build("youtube", "v3", credentials=creds)


def upload_video(video_path: str, thumb_path: str, title: str,
                 description: str, tags: list,
                 credentials_file: str, token_file: str) -> str:
    yt = get_service(credentials_file, token_file)
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
