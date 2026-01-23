import re


def clean_html(text):
    if not text:
        return ""
    cleaned = str(text).replace("<br>", " ").replace("&nbsp;", " ").replace("\n", " ")
    cleaned = re.sub("<[^<]+?>", "", cleaned)
    return cleaned.strip()
