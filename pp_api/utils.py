import requests
import os


def get_session(session, auth_data):
    if session is None:
        assert auth_data is not None
        session = requests.session()
    if auth_data is not None:
        session.auth = auth_data
    return session


def get_auth_data():
    username = os.getenv('pp_user')
    pw = os.getenv('pp_password')
    auth_data = (username, pw)
    assert username and pw
    return auth_data
