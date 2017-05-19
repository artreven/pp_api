import requests


def get_session(session, auth_data):
    if session is None:
        assert auth_data is not None
        session = requests.session()
    if auth_data is not None:
        session.auth = auth_data
    return session
