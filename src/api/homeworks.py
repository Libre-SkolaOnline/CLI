def get_homework(api):
    return api.client.get(
        f"v1/students/{api.person_id}/homeworks", params={"Filter": "active"}
    )
