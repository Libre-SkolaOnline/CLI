def get_behaviors(api):
    return api.client.get(
        f"v1/students/{api.person_id}/behaviors", params={"RecordsFilter": "all"}
    )
