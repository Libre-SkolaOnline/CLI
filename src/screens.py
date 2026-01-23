import logging
from textual import work
from textual.app import App, ComposeResult, on
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    TabPane,
    TabbedContent,
)

from .api import SolApi
from .config import DEBUG


class LoginScreen(Screen):
    CSS = """
    LoginScreen { align: center middle; background: $surface; }
    #login-box { width: 50; height: auto; border: heavy $primary; padding: 2; background: $panel; }
    Input { margin-bottom: 1; }
    Button { width: 100%; margin-top: 1; }
    .title { text-align: center; text-style: bold; margin-bottom: 2; color: $secondary; }
    """

    def __init__(self, api: SolApi):
        super().__init__()
        self.api = api

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="login-box"):
                yield Label("Škola Online", classes="title")
                yield Input(placeholder="Uživatelské jméno", id="username")
                yield Input(placeholder="Heslo", password=True, id="password")
                yield Button("Přihlásit se", variant="primary", id="login-btn")

    @on(Button.Pressed, "#login-btn")
    def action_login(self):
        username = self.query_one("#username").value
        password = self.query_one("#password").value
        if not username or not password:
            return
        self.query_one("#login-btn").disabled = True
        self.query_one("#login-btn").label = "Logování..."
        self.run_login(username, password)

    @work(exclusive=True, thread=True)
    def run_login(self, username, password):
        success, msg = self.api.login(username, password)
        if success:
            if self.api.init_user_data():
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

    def __init__(self, api: SolApi):
        super().__init__()
        self.api = api

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
        self.app.sub_title = f"{self.api.full_name} ({self.api.class_name})"
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
        data = self.api.get_grades()
        self.app.call_from_thread(self.update_grades, data)

    @work(thread=True)
    def work_schedule(self):
        data = self.api.get_schedule()
        self.app.call_from_thread(self.update_schedule, data)

    @work(thread=True)
    def work_messages(self):
        data = self.api.get_messages()
        self.app.call_from_thread(self.update_messages, data)

    @work(thread=True)
    def work_homework(self):
        data = self.api.get_homework()
        self.app.call_from_thread(self.update_homework, data)

    @work(thread=True)
    def work_behavior(self):
        data = self.api.get_behaviors()
        self.app.call_from_thread(self.update_behavior, data)

    def update_grades(self, data):
        dt = self.query_one("#grades_table", DataTable)
        dt.clear(columns=True)
        dt.add_columns("Datum", "Předmět", "Známka", "Váha", "Téma")

        rows = []
        if data and "marks" in data:
            if DEBUG:
                logging.info("UI: Marks count: %s", len(data["marks"]))
            subjects = {subject["id"]: subject["name"] for subject in data.get("subjects", [])}
            for mark in data["marks"]:
                subject = str(subjects.get(mark["subjectId"], "?"))
                raw = str(mark.get("markText", "?"))

                if raw == "1":
                    value = "[bold green]1[/]"
                elif raw == "5":
                    value = "[bold red]5[/]"
                elif raw == "Sl":
                    value = "[cyan]Slovní[/]"
                else:
                    value = raw

                date = str(mark.get("markDate", ""))[:10]
                rows.append((date, subject, value, str(mark.get("weight", "")), str(mark.get("theme", ""))))

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
        if data and "days" in data:
            for day in data["days"]:
                day_name = str(day.get("date", ""))[:10]
                rows.append((f"[bold white on blue]{day_name}[/]", "", "", ""))

                schedules = sorted(day.get("schedules", []), key=lambda item: item["beginTime"])
                for schedule in schedules:
                    time_range = f"{schedule['beginTime'][11:16]}-{schedule['endTime'][11:16]}"
                    subject = schedule.get("subject", {}).get("name") or schedule.get("hourType", {}).get("displayName", "Info")
                    room = schedule.get("room", {}).get("abbrev", "")
                    rows.append(("", time_range, str(subject), f"[yellow]{room}[/]"))

        if rows:
            dt.add_rows(rows)
            self.query_one("#status_bar", Label).update("Rozvrh načten.")
        else:
            dt.add_row("", "", "Žádný rozvrh", "")

    def update_messages(self, messages):
        dt = self.query_one("#msg_table", DataTable)
        dt.clear(columns=True)
        dt.add_columns("Směr", "Datum", "Osoba", "Předmět", "Text")

        rows = []
        if messages:
            if DEBUG:
                logging.info("UI: Msgs count: %s", len(messages))
            for message in messages:
                direction = "[bold green]←[/]" if message["dir"] == "IN" else "[bold yellow]→[/]"
                date = str(message.get("sentDate", ""))[:16].replace("T", " ")

                if message["dir"] == "IN":
                    person = message.get("sender", {}).get("name", str(message.get("senderName", "?")))
                else:
                    person = str(message.get("recipientName", "..."))

                text = self.api.clean_html(message.get("text") or message.get("body"))[:50] + "..."
                rows.append((direction, date, str(person), str(message.get("subject", "")), text))

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
        if data and "homeworks" in data:
            for homework in data["homeworks"]:
                subject = str(homework.get("subject", {}).get("name", "Předmět"))
                date_to = f"[red]{str(homework.get('dateTo', ''))[:10]}[/]"
                topic = str(homework.get("topic", ""))
                description = self.api.clean_html(
                    homework.get("detailedDescription") or homework.get("text")
                )[:60] + "..."
                rows.append((subject, date_to, topic, description))

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
        if data and "behaviors" in data:
            for behavior in data["behaviors"]:
                date = str(behavior.get("date", ""))[:10]
                kind = f"[bold]{behavior.get('kindOfBehaviorName', 'Info')}[/]"
                reason = behavior.get("behaviorReason", "") or "Bez popisu"
                rows.append((date, kind, reason))

        if rows:
            dt.add_rows(rows)
        else:
            dt.add_row("-", "Žádné záznamy", "-")
