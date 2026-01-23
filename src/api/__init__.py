from .behaviors import get_behaviors
from .client import ApiClient
from .homeworks import get_homework
from .mark_detail import get_mark_detail
from .marks import get_grades
from .messages import get_messages
from .schedule import get_schedule
from .user import init_user_data
from .utils import clean_html


class SolApi:
    def __init__(self):
        self.client = ApiClient()
        self.person_id = None
        self.full_name = None
        self.semester_id = None
        self.class_name = None

    def login(self, username, password):
        return self.client.login(username, password)

    def init_user_data(self):
        return init_user_data(self)

    def get_grades(self):
        return get_grades(self)

    def get_schedule(self):
        return get_schedule(self)

    def get_homework(self):
        return get_homework(self)

    def get_messages(self):
        return get_messages(self)

    def get_behaviors(self):
        return get_behaviors(self)

    def get_mark_detail(self, mark_id):
        return get_mark_detail(self, mark_id)

    def get_notifications(self):
        return get_notifications(self)

    @staticmethod
    def clean_html(text):
        return clean_html(text)
