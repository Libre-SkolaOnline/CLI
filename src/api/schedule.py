from datetime import datetime, timedelta


def get_schedule(api):
    today = datetime.now()
    date_from = today.strftime("%Y-%m-%dT00:00:00")
    date_to = (today + timedelta(days=7)).strftime("%Y-%m-%dT00:00:00")
    return api.client.get(
        "v1/timeTable",
        params={"StudentId": api.person_id, "DateFrom": date_from, "DateTo": date_to},
    )
