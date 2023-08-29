# notify.py

import requests

def send_line_notify(token, msg, img):
    """Send message and image to LINE Notify."""
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        'message': msg,
        'imageThumbnail': img,
        'imageFullsize': img
    }
    response = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=payload)
    return response.status_code
