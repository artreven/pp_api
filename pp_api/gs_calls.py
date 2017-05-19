import requests

import utils as u


def create(id, title, author, server, auth_data=None, session=None, **kwargs):
    suffix = '/GraphSearch/api/content/create'
    data = {
        'identifier': id,
        'title': title,
        'author': author
    }
    data.update(kwargs)
    session = u.get_session(session, auth_data)
    r = session.post(
        server + suffix,
        json=data,
    )
    r.raise_for_status()
    return r


if __name__ == '__main__':
    import server_data.profit as server_info
    import virtuoso_calls as vc
    g_guardian = 'https://content.guardianapis.com/money'
    q_guardian = """
    select distinct ?s ?date ?trailtext ?headline where {
      ?s ?p ?o . 
      ?s <http://schema.semantic-web.at#date> ?date .
      ?s <http://schema.semantic-web.at#trail-text> ?trailtext .
      ?s <http://schema.semantic-web.at#headline> ?headline .
    }
    """
    rs = vc.query_sparql_endpoint(
        server_info.sparql_endpoint, g_guardian, q_guardian
    )
    username = input('Username: ')
    pw = input('Password: ')
    auth_data = (username, pw)
    for r in rs:
        id, date, trailtext, headline = r
        print(id, date, trailtext, headline)
        session = u.get_session(session=None, auth_data=auth_data)
        r = create(
            id=id, title=headline, author=g_guardian,
            server=server_info.server,
            text=trailtext, session=session
        )
