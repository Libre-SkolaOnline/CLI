import logging
from typing import Optional

import requests

from ..config import BASE_URL, CLIENT_ID, DEBUG, TOKEN_URL


class ApiClient:
    def __init__(self):
        self.token: Optional[str] = None

    def login(self, username: str, password: str):
        if DEBUG:
            logging.info("Login: %s", username)
        payload = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "scope": "openid offline_access profile sol_api",
            "client_id": CLIENT_ID,
        }
        try:
            response = requests.post(
                TOKEN_URL,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                return True, "OK"
            return False, f"Error: {response.status_code}"
        except Exception as exc:
            return False, str(exc)

    def get(self, endpoint: str, params=None):
        if not self.token:
            return None
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        try:
            response = requests.get(
                f"{BASE_URL}/{endpoint}", headers=headers, params=params
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
