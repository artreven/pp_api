import requests
import os


def get_session(session, auth_data):
    if session is None:
        if auth_data is None:
            auth_data = get_auth_data()
        session = requests.session()
    if auth_data is not None:
        session.auth = auth_data
    return session


def get_auth_data(env_username='PP_USER', env_password='PP_PASSWORD'):
    username = os.getenv(env_username)
    pw = os.getenv(env_password)
    auth_data = (username, pw)
    assert username and pw
    return auth_data
