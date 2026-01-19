import requests
import re
import logging
from datetime import datetime, timedelta
from textual.app import App, ComposeResult, on
from textual.containers import Center, Vertical
from textual.widgets import (
    Header, Footer, Input, Button, Label, TabbedContent, TabPane, 
    DataTable
)
from textual.screen import Screen
from textual import work

DEBUG = False

if DEBUG:
    logging.basicConfig(
        filename='debug.log', 
        level=logging.INFO, 
        format='%(asctime)s - %(message)s',
        force=True
    )
else:
    logging.disable(logging.CRITICAL)

BASE_URL = "https://aplikace.skolaonline.cz/solapi/api"
TOKEN_URL = f"{BASE_URL}/connect/token"
CLIENT_ID = "test_client"

class SolApi:
    def __init__(self):
        self.token = None
        self.person_id = None
        self.full_name = None
        self.semester_id = None
        self.class_name = None

    def login(self, username, password):
        if DEBUG: logging.info(f"Login: {username}")
        payload = {
            'grant_type': 'password', 'username': username, 'password': password,
            'scope': 'openid offline_access profile sol_api', 'client_id': CLIENT_ID
        }
        try:
            r = requests.post(TOKEN_URL, data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
            if r.status_code == 200:
                self.token = r.json()['access_token']
                return True, "OK"
            return False, f"Error: {r.status_code}"
        except Exception as e:
            return False, str(e)

    def _get(self, endpoint, params=None):
        if not self.token: return None
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        try:
            r = requests.get(f"{BASE_URL}/{endpoint}", headers=headers, params=params)
            return r.json() if r.status_code == 200 else None
        except:
            return None

    def init_user_data(self):
        user = self._get("v1/user")
        if not user: return False
        self.person_id = user.get('personID')
        self.full_name = user.get('fullName')
        self.class_name = user.get('class', {}).get('abbrev', '')

        meta = self._get("v1/timeTable/codeLists", params={'studentId': self.person_id})
        if meta and 'semester' in meta:
            now = datetime.now().strftime("%Y-%m-%d")
            for s in meta['semester']:
                if s['dateFrom'][:10] <= now <= s['dateTo'][:10]:
                    self.semester_id = s['id']
                    break
            if not self.semester_id and meta['semester']:
                self.semester_id = meta['semester'][-1]['id']
        
        if DEBUG: logging.info(f"User: {self.full_name}, Sem: {self.semester_id}")
        return True

    def get_grades(self):
        return self._get(f"v1/students/{self.person_id}/marks/list", 
                         params={'SemesterId': self.semester_id, 'SigningFilter': 'all', 'Pagination.PageSize': 100})

    def get_schedule(self):
        today = datetime.now()
        d_from = today.strftime('%Y-%m-%dT00:00:00')
        d_to = (today + timedelta(days=7)).strftime('%Y-%m-%dT00:00:00')
        return self._get("v1/timeTable", params={'StudentId': self.person_id, 'DateFrom': d_from, 'DateTo': d_to})

    def get_homework(self):
        return self._get(f"v1/students/{self.person_id}/homeworks", params={'Filter': 'active'})

    def get_messages(self):
        msgs = []
        rx = self._get("v1/messages/received", params={'Pagination.PageSize': 20})
        if rx and 'messages' in rx: 
            for m in rx['messages']: m['dir'] = 'IN'; msgs.append(m)
        tx = self._get("v1/messages/sent", params={'Pagination.PageSize': 20})
        if tx and 'messages' in tx: 
            for m in tx['messages']: m['dir'] = 'OUT'; msgs.append(m)
        msgs.sort(key=lambda x: x.get('sentDate', ''), reverse=True)
        return msgs

    def get_behaviors(self):
        return self._get(f"v1/students/{self.person_id}/behaviors", params={'RecordsFilter': 'all'})

    def clean_html(self, text):
        if not text: return ""
        text = str(text).replace("<br>", " ").replace("&nbsp;", " ").replace("\n", " ")
        text = re.sub('<[^<]+?>', '', text)
        return text.strip()

api = SolApi()

class LoginScreen(Screen):
    CSS = """
    LoginScreen { align: center middle; background: $surface; }
    #login-box { width: 50; height: auto; border: heavy $primary; padding: 2; background: $panel; }
    Input { margin-bottom: 1; }
    Button { width: 100%; margin-top: 1; }
    .title { text-align: center; text-style: bold; margin-bottom: 2; color: $secondary; }
    """

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="login-box"):
                yield Label("Škola Online", classeimport requests
import re
import logging
from datetime import datetime, timedelta

from textual.app import App, ComposeResult, on
from textual.containers import Center, Vertical
from textual.widgets import (
    Header, Footer, Input, Button, Label, TabbedContent, TabPane, 
    DataTable
)
from textual.screen import Screen
from textual import work

DEBUG = True

if DEBUG:
    logging.basicConfig(
        filename='debug.log', 
        level=logging.INFO, 
        format='%(asctime)s - %(message)s',
        force=True
    )
else:
    logging.disable(logging.CRITICAL)

BASE_URL = "https://aplikace.skolaonline.cz/solapi/api"
TOKEN_URL = f"{BASE_URL}/connect/token"
CLIENT_ID = "test_client"

class SolApi:
    def __init__(self):
        self.token = None
        self.person_id = None
        self.full_name = None
        self.semester_id = None
        self.class_name = None

    def login(self, username, password):
        if DEBUG: logging.info(f"Login: {username}")
        payload = {
            'grant_type': 'password', 'username': username, 'password': password,
            'scope': 'openid offline_access profile sol_api', 'client_id': CLIENT_ID
        }
        try:
            r = requests.post(TOKEN_URL, data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
            if r.status_code == 200:
                self.token = r.json()['access_token']
                return True, "OK"
            return False, f"Error: {r.status_code}"
        except Exception as e:
            return False, str(e)

    def _get(self, endpoint, params=None):
        if not self.token: return None
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        try:
            r = requests.get(f"{BASE_URL}/{endpoint}", headers=headers, params=params)
            return r.json() if r.status_code == 200 else None
        except:
            return None

    def init_user_data(self):
        user = self._get("v1/user")
        if not user: return False
        self.person_id = user.get('personID')
        self.full_name = user.get('fullName')
        self.class_name = user.get('class', {}).get('abbrev', '')

        meta = self._get("v1/timeTable/codeLists", params={'studentId': self.person_id})
        if meta and 'semester' in meta:
            now = datetime.now().strftime("%Y-%m-%d")
            for s in meta['semester']:
                if s['dateFrom'][:10] <= now <= s['dateTo'][:10]:
                    self.semester_id = s['id']
                    break
            if not self.semester_id and meta['semester']:
                self.semester_id = meta['semester'][-1]['id']
        
        if DEBUG: logging.info(f"User: {self.full_name}, Sem: {self.semester_id}")
        return True

    def get_grades(self):
        return self._get(f"v1/students/{self.person_id}/marks/list", 
                         params={'SemesterId': self.semester_id, 'SigningFilter': 'all', 'Pagination.PageSize': 100})

    def get_schedule(self):
        today = datetime.now()
        d_from = today.strftime('%Y-%m-%dT00:00:00')
        d_to = (today + timedelta(days=7)).strftime('%Y-%m-%dT00:00:00')
        return self._get("v1/timeTable", params={'StudentId': self.person_id, 'DateFrom': d_from, 'DateTo': d_to})

    def get_homework(self):
        return self._get(f"v1/students/{self.person_id}/homeworks", params={'Filter': 'active'})

    def get_messages(self):
        msgs = []
        rx = self._get("v1/messages/received", params={'Pagination.PageSize': 20})
        if rx and 'messages' in rx: 
            for m in rx['messages']: m['dir'] = 'IN'; msgs.append(m)
        tx = self._get("v1/messages/sent", params={'Pagination.PageSize': 20})
        if tx and 'messages' in tx: 
            for m in tx['messages']: m['dir'] = 'OUT'; msgs.append(m)
        msgs.sort(key=lambda x: x.get('sentDate', ''), reverse=True)
        return msgs

    def get_behaviors(self):
        return self._get(f"v1/students/{self.person_id}/behaviors", params={'RecordsFilter': 'all'})

    def clean_html(self, text):
        if not text: return ""
        text = str(text).replace("<br>", " ").replace("&nbsp;", " ").replace("\n", " ")
        text = re.sub('<[^<]+?>', '', text)
        return text.strip()

api = SolApi()

class LoginScreen(Screen):
    CSS = """
    LoginScreen { align: center middle; background: $surface; }
    #login-box { width: 50; height: auto; border: heavy $primary; padding: 2; background: $panel; }
    Input { margin-bottom: 1; }
    Button { width: 100%; margin-top: 1; }
    .title { text-align: center; text-style: bold; margin-bottom: 2; color: $secondary; }
    """

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="login-box"):
                yield Label("Škola Online", classes="title")
                yield Input(placeholder="Uživatelské jméno", id="username")
                yield Input(placeholder="Heslo", password=True, id="password")
                yield Button("Přihlásit se", variant="primary", id="login-btn")

    @on(Button.Pressed, "#login-btn")
    def action_login(self):
        u = self.query_one("#username").value
        p = self.query_one("#password").value
        if not u or not p: returnŠkola O
        self.query_one("#login-btn").disabled = True
        self.query_one("#login-btn").label = "Logování..."
        self.run_login(u, p)

    @work(exclusive=True, thread=True)
    def run_login(self, u, p):
        success, msg = api.login(u, p)
        if success:
            if api.init_user_data():
                self.app.call_from_thread(self.app.switch_to_dashboard)
            else:
                self.app.call_from_thread(self.app.notify, "Chyba profilu", severity="error")
                self.app.call_from_thread(self.reset_btn)
        else:
            self.app.call_from_thread(self.app.notify, f"Chyba: {msg}", severity="error")
            self.app.call_from_thread(self.reset_btn)

    def reset_btn(self):
        btn = self.query_one("#login-btn")
        btn.disabled = False
        btn.label = "Přihlásit se"

class Dashboard(Screen):
    CSS = """
    DataTable { 
        height: 1fr; 
        width: 100%;
        border: solid $secondary; 
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Label("Načítám...", id="status_bar")
        
        with TabbedContent(initial="grades"):
            with TabPane("📝 Známky", id="grades"):
                yield DataTable(id="grades_table", zebra_stripes=True, cursor_type="row")
            with TabPane("📅 Rozvrh", id="schedule"):
                yield DataTable(id="schedule_table", zebra_stripes=True)
            with TabPane("📩 Zprávy", id="messages"):
                yield DataTable(id="msg_table", zebra_stripes=True, cursor_type="row")
            with TabPane("🏠 Úkoly", id="homework"):
                yield DataTable(id="hw_table", zebra_stripes=True, cursor_type="row")
            with TabPane("⚠️ Chování", id="behavior"):
                 yield DataTable(id="behavior_table", zebra_stripes=True)
        yield Footer()

    def on_mount(self):
        self.app.sub_title = f"{api.full_name} ({api.class_name})"
        self.trigger_load("grades")

    @on(TabbedContent.TabActivated)
    def on_tab_switch(self, event: TabbedContent.TabActivated):
        self.trigger_load(event.pane.id)

    def trigger_load(self, tab_id):
        self.query_one("#status_bar", Label).update(f"Načítám data: {tab_id}...")
        
        if tab_id == "grades":
            self.work_grades()
        elif tab_id == "schedule":
            self.work_schedule()
        elif tab_id == "messages":
            self.work_messages()
        elif tab_id == "homework":
            self.work_homework()
        elif tab_id == "behavior":
            self.work_behavior()

    @work(thread=True)
    def work_grades(self):
        data = api.get_grades()
        self.app.call_from_thread(self.update_grades, data)

    @work(thread=True)
    def work_schedule(self):
        data = api.get_schedule()
        self.app.call_from_thread(self.update_schedule, data)

    @work(thread=True)
    def work_messages(self):
        data = api.get_messages()
        self.app.call_from_thread(self.update_messages, data)

    @work(thread=True)
    def work_homework(self):
        data = api.get_homework()
        self.app.call_from_thread(self.update_homework, data)

    @work(thread=True)
    def work_behavior(self):
        data = api.get_behaviors()
        self.app.call_from_thread(self.update_behavior, data)

    def update_grades(self, data):
        dt = self.query_one("#grades_table", DataTable)
        dt.clear(columns=True) 
        dt.add_columns("Datum", "Předmět", "Známka", "Váha", "Téma")
        
        rows = []
        if data and 'marks' in data:
            if DEBUG: logging.info(f"UI: Marks count: {len(data['marks'])}")
            subjects = {s['id']: s['name'] for s in data.get('subjects', [])}
            for m in data['marks']:
                subj = str(subjects.get(m['subjectId'], "?"))
                raw = str(m.get('markText', '?'))
                
                if raw == '1': val = "[bold green]1[/]"
                elif raw == '5': val = "[bold red]5[/]"
                elif raw == 'Sl': val = "[cyan]Slovní[/]"
                else: val = raw
                
                date = str(m.get('markDate', ''))[:10]
                rows.append((date, subj, val, str(m.get('weight', '')), str(m.get('theme', ''))))
        
        if rows:
            dt.add_rows(rows)
            self.query_one("#status_bar", Label).update(f"Známky: {len(rows)}")
        else:
            dt.add_row("---", "Žádné známky", "", "", "")
            self.query_one("#status_bar", Label).update("Žádné známky.")

    def update_schedule(self, data):
        dt = self.query_one("#schedule_table", DataTable)
        dt.clear(columns=True)
        dt.add_columns("Den", "Čas", "Předmět", "Učebna")

        rows = []
        if data and 'days' in data:
            for day in data['days']:
                day_name = str(day.get('date', ''))[:10]
                rows.append((f"[bold white on blue]{day_name}[/]", "", "", ""))
                
                schedules = sorted(day.get('schedules', []), key=lambda x: x['beginTime'])
                for s in schedules:
                    time = f"{s['beginTime'][11:16]}-{s['endTime'][11:16]}"
                    subj = s.get('subject', {}).get('name') or s.get('hourType', {}).get('displayName', 'Info')
                    room = s.get('room', {}).get('abbrev', '')
                    rows.append(("", time, str(subj), f"[yellow]{room}[/]"))
        
        if rows:
            dt.add_rows(rows)
            self.query_one("#status_bar", Label).update("Rozvrh načten.")
        else:
             dt.add_row("", "", "Žádný rozvrh", "")

    def update_messages(self, msgs):
        dt = self.query_one("#msg_table", DataTable)
        dt.clear(columns=True)
        dt.add_columns("Směr", "Datum", "Osoba", "Předmět", "Text")

        rows = []
        if DEBUG: logging.info(f"UI: Msgs count: {len(msgs)}")
        for m in msgs:
            direction = "[bold green]←[/]" if m['dir'] == 'IN' else "[bold yellow]→[/]"
            date = str(m.get('sentDate', ''))[:16].replace('T', ' ')
            
            if m['dir'] == 'IN':
                person = m.get('sender', {}).get('name', str(m.get('senderName', '?')))
            else:
                person = str(m.get('recipientName', '...'))

            text = api.clean_html(m.get('text') or m.get('body'))[:50] + "..."
            rows.append((direction, date, str(person), str(m.get('subject', '')), text))
            
        if rows:
            dt.add_rows(rows)
            self.query_one("#status_bar", Label).update(f"Zprávy: {len(rows)}")
        else:
             dt.add_row("-", "-", "Žádné zprávy", "-", "-")

    def update_homework(self, data):
        dt = self.query_one("#hw_table", DataTable)
        dt.clear(columns=True)
        dt.add_columns("Předmět", "Do kdy", "Téma", "Popis")

        rows = []
        if data and 'homeworks' in data:
            for hw in data['homeworks']:
                subj = str(hw.get('subject', {}).get('name', 'Předmět'))
                date = f"[red]{str(hw.get('dateTo', ''))[:10]}[/]"
                topic = str(hw.get('topic', ''))
                desc = api.clean_html(hw.get('detailedDescription') or hw.get('text'))[:60] + "..."
                rows.append((subj, date, topic, desc))
        
        if rows:
            dt.add_rows(rows)
            self.query_one("#status_bar", Label).update(f"Úkoly: {len(rows)}")
        else:
            dt.add_row("-", "-", "Žádné úkoly", "-")

    def update_behavior(self, data):
        dt = self.query_one("#behavior_table", DataTable)
        dt.clear(columns=True)
        dt.add_columns("Datum", "Typ", "Důvod")
            
        rows = []
        if data and 'behaviors' in data:
            for b in data['behaviors']:
                date = str(b.get('date', ''))[:10]
                kind = f"[bold]{b.get('kindOfBehaviorName', 'Info')}[/]"
                reason = b.get('behaviorReason', '') or "Bez popisu"
                rows.append((date, kind, reason))
        
        if rows:
            dt.add_rows(rows)
        else:
            dt.add_row("-", "Žádné záznamy", "-")

class SolApp(App):
    CSS = "Screen { background: $surface; }"
    BINDINGS = [("q", "quit", "Ukončit")]

    def on_mount(self):
        self.push_screen(LoginScreen())

    def switch_to_dashboard(self):
        self.push_screen(Dashboard())

if __name__ == "__main__":
    app = SolApp()
    app.run()s="title")
                yield Input(placeholder="Uživatelské jméno", id="username")
                yield Input(placeholder="Heslo", password=True, id="password")
                yield Button("Přihlásit se", variant="primary", id="login-btn")

    @on(Button.Pressed, "#login-btn")
    def action_login(self):
        u = self.query_one("#username").value
        p = self.query_one("#password").value
        if not u or not p: returnŠkola O
        self.query_one("#login-btn").disabled = True
        self.query_one("#login-btn").label = "Logování..."
        self.run_login(u, p)

    @work(exclusive=True, thread=True)
    def run_login(self, u, p):
        success, msg = api.login(u, p)
        if success:
            if api.init_user_data():
                self.app.call_from_thread(self.app.switch_to_dashboard)
            else:
                self.app.call_from_thread(self.app.notify, "Chyba profilu", severity="error")
                self.app.call_from_thread(self.reset_btn)
        else:
            self.app.call_from_thread(self.app.notify, f"Chyba: {msg}", severity="error")
            self.app.call_from_thread(self.reset_btn)

    def reset_btn(self):
        btn = self.query_one("#login-btn")
        btn.disabled = False
        btn.label = "Přihlásit se"

class Dashboard(Screen):
    CSS = """
    DataTable { 
        height: 1fr; 
        width: 100%;
        border: solid $secondary; 
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Label("Načítám...", id="status_bar")
        
        with TabbedContent(initial="grades"):
            with TabPane("📝 Známky", id="grades"):
                yield DataTable(id="grades_table", zebra_stripes=True, cursor_type="row")
            with TabPane("📅 Rozvrh", id="schedule"):
                yield DataTable(id="schedule_table", zebra_stripes=True)
            with TabPane("📩 Zprávy", id="messages"):
                yield DataTable(id="msg_table", zebra_stripes=True, cursor_type="row")
            with TabPane("🏠 Úkoly", id="homework"):
                yield DataTable(id="hw_table", zebra_stripes=True, cursor_type="row")
            with TabPane("⚠️ Chování", id="behavior"):
                 yield DataTable(id="behavior_table", zebra_stripes=True)
        yield Footer()

    def on_mount(self):
        self.app.sub_title = f"{api.full_name} ({api.class_name})"
        self.trigger_load("grades")

    @on(TabbedContent.TabActivated)
    def on_tab_switch(self, event: TabbedContent.TabActivated):
        self.trigger_load(event.pane.id)

    def trigger_load(self, tab_id):
        self.query_one("#status_bar", Label).update(f"Načítám data: {tab_id}...")
        
        if tab_id == "grades":
            self.work_grades()
        elif tab_id == "schedule":
            self.work_schedule()
        elif tab_id == "messages":
            self.work_messages()
        elif tab_id == "homework":
            self.work_homework()
        elif tab_id == "behavior":
            self.work_behavior()

    @work(thread=True)
    def work_grades(self):
        data = api.get_grades()
        self.app.call_from_thread(self.update_grades, data)

    @work(thread=True)
    def work_schedule(self):
        data = api.get_schedule()
        self.app.call_from_thread(self.update_schedule, data)

    @work(thread=True)
    def work_messages(self):
        data = api.get_messages()
        self.app.call_from_thread(self.update_messages, data)

    @work(thread=True)
    def work_homework(self):
        data = api.get_homework()
        self.app.call_from_thread(self.update_homework, data)

    @work(thread=True)
    def work_behavior(self):
        data = api.get_behaviors()
        self.app.call_from_thread(self.update_behavior, data)

    def update_grades(self, data):
        dt = self.query_one("#grades_table", DataTable)
        dt.clear(columns=True) 
        dt.add_columns("Datum", "Předmět", "Známka", "Váha", "Téma")
        
        rows = []
        if data and 'marks' in data:
            if DEBUG: logging.info(f"UI: Marks count: {len(data['marks'])}")
            subjects = {s['id']: s['name'] for s in data.get('subjects', [])}
            for m in data['marks']:
                subj = str(subjects.get(m['subjectId'], "?"))
                raw = str(m.get('markText', '?'))
                
                if raw == '1': val = "[bold green]1[/]"
                elif raw == '5': val = "[bold red]5[/]"
                elif raw == 'Sl': val = "[cyan]Slovní[/]"
                else: val = raw
                
                date = str(m.get('markDate', ''))[:10]
                rows.append((date, subj, val, str(m.get('weight', '')), str(m.get('theme', ''))))
        
        if rows:
            dt.add_rows(rows)
            self.query_one("#status_bar", Label).update(f"Známky: {len(rows)}")
        else:
            dt.add_row("---", "Žádné známky", "", "", "")
            self.query_one("#status_bar", Label).update("Žádné známky.")

    def update_schedule(self, data):
        dt = self.query_one("#schedule_table", DataTable)
        dt.clear(columns=True)
        dt.add_columns("Den", "Čas", "Předmět", "Učebna")

        rows = []
        if data and 'days' in data:
            for day in data['days']:
                day_name = str(day.get('date', ''))[:10]
                rows.append((f"[bold white on blue]{day_name}[/]", "", "", ""))
                
                schedules = sorted(day.get('schedules', []), key=lambda x: x['beginTime'])
                for s in schedules:
                    time = f"{s['beginTime'][11:16]}-{s['endTime'][11:16]}"
                    subj = s.get('subject', {}).get('name') or s.get('hourType', {}).get('displayName', 'Info')
                    room = s.get('room', {}).get('abbrev', '')
                    rows.append(("", time, str(subj), f"[yellow]{room}[/]"))
        
        if rows:
            dt.add_rows(rows)
            self.query_one("#status_bar", Label).update("Rozvrh načten.")
        else:
             dt.add_row("", "", "Žádný rozvrh", "")

    def update_messages(self, msgs):
        dt = self.query_one("#msg_table", DataTable)
        dt.clear(columns=True)
        dt.add_columns("Směr", "Datum", "Osoba", "Předmět", "Text")

        rows = []
        if DEBUG: logging.info(f"UI: Msgs count: {len(msgs)}")
        for m in msgs:
            direction = "[bold green]←[/]" if m['dir'] == 'IN' else "[bold yellow]→[/]"
            date = str(m.get('sentDate', ''))[:16].replace('T', ' ')
            
            if m['dir'] == 'IN':
                person = m.get('sender', {}).get('name', str(m.get('senderName', '?')))
            else:
                person = str(m.get('recipientName', '...'))

            text = api.clean_html(m.get('text') or m.get('body'))[:50] + "..."
            rows.append((direction, date, str(person), str(m.get('subject', '')), text))
            
        if rows:
            dt.add_rows(rows)
            self.query_one("#status_bar", Label).update(f"Zprávy: {len(rows)}")
        else:
             dt.add_row("-", "-", "Žádné zprávy", "-", "-")

    def update_homework(self, data):
        dt = self.query_one("#hw_table", DataTable)
        dt.clear(columns=True)
        dt.add_columns("Předmět", "Do kdy", "Téma", "Popis")

        rows = []
        if data and 'homeworks' in data:
            for hw in data['homeworks']:
                subj = str(hw.get('subject', {}).get('name', 'Předmět'))
                date = f"[red]{str(hw.get('dateTo', ''))[:10]}[/]"
                topic = str(hw.get('topic', ''))
                desc = api.clean_html(hw.get('detailedDescription') or hw.get('text'))[:60] + "..."
                rows.append((subj, date, topic, desc))
        
        if rows:
            dt.add_rows(rows)
            self.query_one("#status_bar", Label).update(f"Úkoly: {len(rows)}")
        else:
            dt.add_row("-", "-", "Žádné úkoly", "-")

    def update_behavior(self, data):
        dt = self.query_one("#behavior_table", DataTable)
        dt.clear(columns=True)
        dt.add_columns("Datum", "Typ", "Důvod")
            
        rows = []
        if data and 'behaviors' in data:
            for b in data['behaviors']:
                date = str(b.get('date', ''))[:10]
                kind = f"[bold]{b.get('kindOfBehaviorName', 'Info')}[/]"
                reason = b.get('behaviorReason', '') or "Bez popisu"
                rows.append((date, kind, reason))
        
        if rows:
            dt.add_rows(rows)
        else:
            dt.add_row("-", "Žádné záznamy", "-")

class SolApp(App):
    CSS = "Screen { background: $surface; }"
    BINDINGS = [("q", "quit", "Ukončit")]

    def on_mount(self):
        self.push_screen(LoginScreen())

    def switch_to_dashboard(self):
        self.push_screen(Dashboard())

if __name__ == "__main__":
    app = SolApp()
    app.run()