import requests

from decouple import config


def get_session(session, auth_data):
    if session is None:
        if auth_data is None:
            auth_data = get_auth_data()
        session = requests.session()
    if auth_data is not None:
        session.auth = auth_data
    return session


def get_auth_data(env_username='PP_USER', env_password='PP_PASSWORD'):
    username = config(env_username)
    pw = config(env_password)
    auth_data = (username, pw)
    assert username and pw
    return auth_data


def subdict(fromdict, fields, default=None, *, force=False):
    """
    Return a dictionary with the specified selection of keys from `fromdict`.
    If `default` is not None or `force` is true, set missing requested keys to
    the value of `default`.
    (Argument `force` is only needed if the desired default is None)
    """
    if default is not None:
        force = True
    return { k: fromdict.get(k, default) for k in fields if k in fromdict or force }
