from src.headers import BAD_REQUEST, NOT_USER

import pytest
import requests
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def not_user_id():
    return str(uuid.uuid4())

@pytest.fixture
def response_without_users():
    return {"data": []}


@pytest.fixture
def bad_body_in_post_users():
    return {"name": "Test POST", "description": "Other user..."}


"""
In order, the following are executed:
    1) Initialize the database with a test user.
    2) Run the test.
    3) Delete the test user.  
"""
@pytest.fixture
def setup_and_cleanup_test_data(user):
    #execute_query(INSERT_QUERY, user)

    yield user["uuid"]  # Se ejecuta el test

    #execute_query(DELETE_QUERY, {"uuid": user["uuid"]})


@pytest.fixture
def bad_request_response(user_with_bad_body):
    return {
        "type": "about:blank",
        "title": BAD_REQUEST,
        "status": 0,
        "detail": f"{BAD_REQUEST} with body: {user_with_bad_body}",
        "instance": f"/users",
    }


@pytest.fixture
def not_user_response(not_user_id):
    return {
        "type": "about:blank",
        "title": NOT_USER,
        "status": 0,
        "detail": f"The user with uuid {not_user_id} was not found",
        "instance": f"/users/{not_user_id}",
    }


def test_get_users_without_users(response_without_users):
    url = f"{os.getenv("URL")}"

    response = requests.get(url)
    response_data = response.json()

    assert response.status_code == 200
    assert response_without_users == response_data
