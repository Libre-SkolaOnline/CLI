def get_mark_detail(api, mark_id):
    return api.client.get(
        f"v1/student/marks/{mark_id}",
        params={"StudentId": api.person_id}
    )
