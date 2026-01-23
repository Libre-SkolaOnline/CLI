def get_grades(api):
    return api.client.get(
        f"v1/students/{api.person_id}/marks/list",
        params={
            "SemesterId": api.semester_id,
            "SigningFilter": "all",
            "Pagination.PageSize": 100,
        },
    )
