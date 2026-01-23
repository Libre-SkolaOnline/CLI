from datetime import datetime

from ..config import DEBUG


def init_user_data(api):
    user = api.client.get("v1/user")
    if not user:
        return False
    api.person_id = user.get("personID")
    api.full_name = user.get("fullName")
    api.class_name = user.get("class", {}).get("abbrev", "")

    meta = api.client.get("v1/timeTable/codeLists", params={"studentId": api.person_id})
    if meta and "semester" in meta:
        now = datetime.now().strftime("%Y-%m-%d")
        for semester in meta["semester"]:
            if semester["dateFrom"][:10] <= now <= semester["dateTo"][:10]:
                api.semester_id = semester["id"]
                break
        if not api.semester_id and meta["semester"]:
            api.semester_id = meta["semester"][-1]["id"]

    if DEBUG:
        import logging

        logging.info("User: %s, Sem: %s", api.full_name, api.semester_id)
    return True
