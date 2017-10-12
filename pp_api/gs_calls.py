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


def get_fields(server, auth_data=None, session=None):
    suffix = '/GraphSearch/admin/config/fields'
    session = u.get_session(session, auth_data)
    r = session.get(
        server + suffix,
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
    import os
    username = os.getenv('pp_user')
    pw = os.getenv('pp_password')
    auth_data = (username, pw)

    ###
    # search for a particular article specified by id
    search_filters = [
        {'field': 'identifier',
         'value': 'http://money.cnn.com/2017/05/03/retirement/dollar-cost-averaging/index.html?section=money_retirement'}
    ]
    r = search(
        server=profit_info.server, auth_data=auth_data,
        count=10000,
        searchFilters=search_filters,
        documentFacets=['all'],
    )
    print(len(r.json()['results']))

    # Filter by a concept
    fields = get_fields(server=profit_info.server, auth_data=auth_data).json()['searchFields']
    print(fields[0])
    for i in range(10):
        cpt_uri = 'http://profit.poolparty.biz/profit_thesaurus/' + fields[i]['field'].split('_')[-1]
        print(cpt_uri)
        search_filters = [
            {'field': 'dyn_uri_all_concepts',
            'value': cpt_uri}
        ]
        r = search(
            server=profit_info.server, auth_data=auth_data,
            count=10000,
            searchFilters=search_filters,
            documentFacets=['all'],
        )
        print(len(r.json()['results']))

    # The author is in 'dyn_lit_author'
    authors_list = list(profit_info.ld_graphs.keys())
    search_filters = [
        {'field': 'dyn_lit_author',
         'value': authors_list[0]}
    ]
    r = search(
        server=profit_info.server, auth_data=auth_data,
        count=100,
        documentFacets=['dyn_lit_author'],
        searchFilters=search_filters,
    )
    print(r.json()['total'])
    # print(r.json())

    # date search
    import datetime
    date_str = '[{} TO NOW]'.format(
        (datetime.datetime.today() - datetime.timedelta(days=90)).isoformat()
    )
    print(date_str)
    search_filters = [
        {'field': 'date',
         'value': date_str}
    ]
    r = search(
        server=profit_info.server, auth_data=auth_data,
        count=100,
        documentFacets=['date'],
        searchFilters=search_filters,
    )
    print(r.json()['total'])
    print(r.json())
