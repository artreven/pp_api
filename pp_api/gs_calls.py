from requests.exceptions import HTTPError

from pp_api import utils as u


def delete(server, auth_data=None, session=None, id=None, source=None):
    if id is not None:
        suffix = '/GraphSearch/api/content/delete/id'
        data = {
            'identifier': id,
        }
    elif source is not None:
        suffix = '/GraphSearch/api/content/delete/source'
        data = {
            'identifier': source,
        }
    else:
        assert 0
    session = u.get_session(session, auth_data)
    r = session.post(
        server + suffix,
        json=data,
    )
    r.raise_for_status()
    return r


def create(id_, title, author, server, auth_data=None, session=None, **kwargs):
    suffix = '/GraphSearch/api/content/create'
    data = {
        'identifier': id_,
        'title': title,
        'author': author
    }
    data.update(kwargs)
    session = u.get_session(session, auth_data)
    r = session.post(
        server + suffix,
        json=data,
    )
    try:
        r.raise_for_status()
    except HTTPError as e:
        print(r.text)
        raise e
    return r


def search(server, auth_data=None, session=None, **kwargs):
    suffix = '/GraphSearch/api/search'
    data = dict()
    if kwargs:
        data.update(**kwargs)
    session = u.get_session(session, auth_data)
    r = session.post(
        server + suffix,
        json=data,
    )
    try:
        r.raise_for_status()
    except HTTPError as e:
        print(r.request.__dict__)
        print(r.text)
        raise e
    return r


if __name__ == '__main__':
    import server_data.profit as profit_info
    import virtuoso_calls as vc
    # username = input('Username: ')
    # pw = input('Password: ')
    # auth_data = (username, pw)
    auth_data = ('revenkoa', 'revenkpp')

    ###
    search_filters = [
        {'field': 'identifier',
         'value': 'http://money.cnn.com/2017/05/03/retirement/dollar-cost-averaging/index.html?section=money_retirement'}
    ]
    r = search(
        server=profit_info.server, auth_data=auth_data,
        count=10000,
        searchFilters=search_filters,
    )
    print(r.request.__dict__)
    print(len(r.json()['results']))
    print(r.json()['total'])

    # The whole text of the article is stored in 'dyn_txt_wholetext'
    # The author is in 'dyn_lit_author'
    # The documentFacets=['all'] returns all the found concepts, try it.
    r = search(
        server=profit_info.server, auth_data=auth_data,
        count=10000,
        documentFacets=['dyn_txt_wholetext', 'dyn_lit_author'],
    )
    print(len(r.json()['results']))
    print(r.json()['total'])
