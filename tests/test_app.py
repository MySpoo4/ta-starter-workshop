import pytest

from app import app, tasks


@pytest.fixture
def client():
    """Provide a configured Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset the in-memory task list before each test."""
    tasks.clear()
    tasks.extend([
        {"id": 1, "title": "Project-1 Report"},
        {"id": 2, "title": "Project-2 MMFs"}
    ])


def test_index(client):
    """Render the task tracker page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Task Tracker" in response.data


def test_get_tasks_includes_default_priority(client):
    """Return Medium for legacy tasks without a stored priority."""
    response = client.get('/api/tasks')
    assert response.status_code == 200

    data = response.get_json()
    assert len(data) == 2
    assert all(task['priority'] == 'Medium' for task in data)


@pytest.mark.parametrize('priority', ['Low', 'Medium', 'High'])
def test_add_task_supports_all_priorities(client, priority):
    """Store and return each supported task priority."""
    response = client.post(
        '/api/tasks',
        json={'title': f'{priority} task', 'priority': priority}
    )

    assert response.status_code == 201
    created_task = response.get_json()
    assert created_task['priority'] == priority

    get_response = client.get('/api/tasks')
    created_tasks = [
        task for task in get_response.get_json()
        if task['id'] == created_task['id']
    ]
    assert created_tasks[0]['priority'] == priority


def test_add_task_defaults_to_medium_priority(client):
    """Use Medium when a task priority is omitted."""
    response = client.post('/api/tasks', json={'title': 'Default task'})

    assert response.status_code == 201
    assert response.get_json()['priority'] == 'Medium'


def test_add_task_rejects_invalid_priority(client):
    """Reject task priorities outside the supported values."""
    response = client.post(
        '/api/tasks',
        json={'title': 'Invalid task', 'priority': 'Urgent'}
    )

    assert response.status_code == 400
    assert response.get_json()['error'] == 'Invalid priority'

    get_response = client.get('/api/tasks')
    assert len(get_response.get_json()) == 2


def test_add_task_missing_title(client):
    """Reject task creation when the title is missing."""
    response = client.post('/api/tasks', json={'wrong_key': 'value'})
    assert response.status_code == 400
    assert 'error' in response.get_json()

    response2 = client.post('/api/tasks', json={})
    assert response2.status_code == 400


def test_delete_task(client):
    """Delete an existing task."""
    response = client.delete('/api/tasks/1')
    assert response.status_code == 200
    get_response = client.get('/api/tasks')
    data = get_response.get_json()
    assert len(data) == 1
    assert data[0]['id'] == 2
