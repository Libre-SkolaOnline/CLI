import logging
import re
from datetime import datetime, timedelta

import requests

from .config import BASE_URL, CLIENT_ID, DEBUG, TOKEN_URL


class SolApi:
    def __init__(self):
        self.token = None
        self.person_id = None
        self.full_name = None
        self.semester_id = None
        self.class_name = None

    def login(self, username, password):
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

    def _get(self, endpoint, params=None):
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

    def init_user_data(self):
        user = self._get("v1/user")
        if not user:
            return False
        self.person_id = user.get("personID")
        self.full_name = user.get("fullName")
        self.class_name = user.get("class", {}).get("abbrev", "")

        meta = self._get("v1/timeTable/codeLists", params={"studentId": self.person_id})
        if meta and "semester" in meta:
            now = datetime.now().strftime("%Y-%m-%d")
            for semester in meta["semester"]:
                if semester["dateFrom"][:10] <= now <= semester["dateTo"][:10]:
                    self.semester_id = semester["id"]
                    break
            if not self.semester_id and meta["semester"]:
                self.semester_id = meta["semester"][-1]["id"]

        if DEBUG:
            logging.info("User: %s, Sem: %s", self.full_name, self.semester_id)
        return True

    def get_grades(self):
        return self._get(
            f"v1/students/{self.person_id}/marks/list",
            params={
                "SemesterId": self.semester_id,
                "SigningFilter": "all",
                "Pagination.PageSize": 100,
            },
        )

    def get_schedule(self):
        today = datetime.now()
        date_from = today.strftime("%Y-%m-%dT00:00:00")
        date_to = (today + timedelta(days=7)).strftime("%Y-%m-%dT00:00:00")
        return self._get(
            "v1/timeTable",
            params={"StudentId": self.person_id, "DateFrom": date_from, "DateTo": date_to},
        )

    def get_homework(self):
        return self._get(
            f"v1/students/{self.person_id}/homeworks", params={"Filter": "active"}
        )

    def get_messages(self):
        messages = []
        received = self._get("v1/messages/received", params={"Pagination.PageSize": 20})
        if received and "messages" in received:
            for message in received["messages"]:
                message["dir"] = "IN"
                messages.append(message)

        sent = self._get("v1/messages/sent", params={"Pagination.PageSize": 20})
        if sent and "messages" in sent:
            for message in sent["messages"]:
                message["dir"] = "OUT"
                messages.append(message)

        messages.sort(key=lambda item: item.get("sentDate", ""), reverse=True)
        return messages

    def get_behaviors(self):
        return self._get(
            f"v1/students/{self.person_id}/behaviors", params={"RecordsFilter": "all"}
        )

    @staticmethod
    def clean_html(text):
        if not text:
            return ""
        cleaned = str(text).replace("<br>", " ").replace("&nbsp;", " ").replace("\n", " ")
        cleaned = re.sub("<[^<]+?>", "", cleaned)
        return cleaned.strip()
