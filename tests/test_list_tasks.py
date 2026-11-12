from sqlalchemy import event


def test_list_tasks_query_count_is_constant(client, db_session):
    # 할 일 개수와 관계없이 쿼리 수가 일정한지 확인해 N+1 재발을 막습니다.
    for i in range(10):
        client.post("/tasks", json={"title": f"t{i}", "tags": [f"tag{i}"]})
    db_session.expunge_all()

    count = 0

    def on_execute(*_):
        nonlocal count
        count += 1

    engine = db_session.get_bind()
    event.listen(engine, "before_cursor_execute", on_execute)
    try:
        res = client.get("/tasks")
    finally:
        event.remove(engine, "before_cursor_execute", on_execute)

    assert res.status_code == 200
    assert len(res.json()) == 10
    assert count == 2  # tasks 1회 + tags 1회


def test_list_tasks_ordered_by_id(client):
    for title in ["첫째", "둘째", "셋째"]:
        client.post("/tasks", json={"title": title, "tags": []})

    ids = [t["id"] for t in client.get("/tasks").json()]
    assert ids == sorted(ids)
