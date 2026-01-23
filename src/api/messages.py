def get_messages(api):
    messages = []
    received = api.client.get("v1/messages/received", params={"Pagination.PageSize": 20})
    if received and "messages" in received:
        for message in received["messages"]:
            message["dir"] = "IN"
            messages.append(message)

    sent = api.client.get("v1/messages/sent", params={"Pagination.PageSize": 20})
    if sent and "messages" in sent:
        for message in sent["messages"]:
            message["dir"] = "OUT"
            messages.append(message)

    messages.sort(key=lambda item: item.get("sentDate", ""), reverse=True)
    return messages
