from requests.exceptions import HTTPError

from pp_api import utils as u
from pp_api import pp_calls


class GraphSearch:
    def __init__(self, server, auth_data=None, session=None):
        self.server = server
        session = u.get_session(session, auth_data)
        self.auth_data = auth_data
        self.session = session

    def delete(self, id_=None, source=None):
        if id_ is not None:
            suffix = '/GraphSearch/api/content/delete/id'
            data = {
                'identifier': id_,
            }
        elif source is not None:
            suffix = '/GraphSearch/api/content/delete/source'
            data = {
                'identifier': source,
            }
        else:
            assert 0
        r = self.session.post(
            self.server + suffix,
            json=data,
        )
        r.raise_for_status()
        return r

    def _create(self, id_, title, author, date, text=None, update=False,
                text_limit=True, **kwargs):
        """

        :param id_: should be a URL starting from protocol (e.g. http://)
        :param title:
        :param author:
        :param date: datetime object
        :param kwargs: any additional fields in key=value format. Fields should exist in GS.
        :return:
        """
        if text_limit and len(text) > 12048:
            text = text[:12000]
        if not update:
            suffix = '/GraphSearch/api/content/create'
        else:
            suffix = '/GraphSearch/api/content/update'
        data = {
            'identifier': id_,
            'title': title,
            'author': author,
            'date': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'text': text,
            'useExtraction': False
        }
        data.update(kwargs)
        r = self.session.post(
            self.server + suffix,
            json=data,
        )
        try:
            r.raise_for_status()
        except HTTPError as e:
            print(r.text)
            raise e
        return r

    def create_with_freqs(self, id_, title, author, date, cpts, text=None, update=False):
        cpt_uris = [x['uri'] for x in cpts]
        cpt_freqs = {
            x['uri'].split("/")[-1]: x['frequencyInDocument'] for x in cpts
        }
        cpt_facets = {
            ('dyn_flt_' + suffix): [freq] for suffix, freq in cpt_freqs.items()
        }
        cpt_facets.update({
            'dyn_uri_all_concepts': cpt_uris
        })
        return self._create(
            id_=id_, title=title, author=author, date=date,
            text=text, facets=cpt_facets,
            update=update
        )

    def extract_and_create(self, pid, id_, title, author, date, text,
                           update=False):
        """
        Extract concepts from the text and create corresponding document with
        concept frequencies.

        :param pid: project id of the thesaurus in PoolParty
        :param id_:
        :param title:
        :param author:
        :param date:
        :param text:
        :return:
        """
        pp = pp_calls.PoolParty(server=self.server, auth_data=self.auth_data)
        r = pp.extract(
            pid=pid, text=text
        )
        cpts = pp_calls.get_cpts_from_response(r)
        self.create_with_freqs(
            id_=id_, title=title, author=author,
            date=date, text=text, cpts=cpts, update=update
        )
        return cpts

    def extract_and_update(self, *args, **kwargs):
        return self.extract_and_create(*args, update=True, **kwargs)

    def _search(self, **kwargs):
        suffix = '/GraphSearch/api/search'
        data = dict()
        if kwargs:
            data.update(**kwargs)
        r = self.session.post(
            self.server + suffix,
            json=data,
        )
        try:
            r.raise_for_status()
        except HTTPError as e:
            print(r.request.__dict__)
            print(r.text)
            raise e
        return r

    def filter_cpt(self, cpt_uri, **kwargs):
        search_filters = [
            {'field': 'dyn_uri_all_concepts',
             'value': cpt_uri}
        ]
        r = self._search(
            searchFilters=search_filters,
            documentFacets=['all'],
            **kwargs
        )
        return r

    def filter_author(self, author, **kwargs):
        search_filters = [
            {'field': 'dyn_lit_author',
             'value': author}
        ]
        r = self._search(
            searchFilters=search_filters,
            documentFacets=['all'],
            **kwargs
        )
        return r

    def filter_id(self, id_, **kwargs):
        search_filters = [
            {'field': 'identifier',
             'value': id_}
        ]
        r = self._search(
            searchFilters=search_filters,
            documentFacets=['all'],
            **kwargs
        )
        return r

    def filter_date(self, start_date=None, finish_date=None, **kwargs):
        """

        :param start: datetime object
        :param finish: datetime object
        :return:
        """
        start_str = (start_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                     if start_date
                     else "1970-01-01T23:00:00.000Z")
        finish_str = (finish_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                      if finish_date
                      else "NOW")
        date_str = '[{start} TO {finish}]'.format(start=start_str, finish=finish_str)
        search_filters = [
            {'field': 'date',
             'value': date_str}
        ]
        r = self._search(
            searchFilters=search_filters,
            documentFacets=['all'],
            **kwargs
        )
        return r

    def get_fields(self):
        suffix = '/GraphSearch/admin/config/fields'
        r = self.session.get(
            self.server + suffix,
        )
        try:
            r.raise_for_status()
        except HTTPError as e:
            print(r.request.__dict__)
            print(r.text)
            raise e
        return r

    def add_field(self, space_id, field, label):
        suffix = '/GraphSearch/admin/suggest/add'
        data = {
            'searchSpaceId': space_id,
            'field': field,
            'label': label
        }
        r = self.session.post(
            self.server + suffix,
            params=data,
            # data=data
        )
        try:
            r.raise_for_status()
        except HTTPError as e:
            print(r.request.__dict__)
            print(r.text)
            raise e
        return r


def sort_by_date(gs_results):
    ans = sorted(
        gs_results,
        key=lambda x: x['date']
    )
    return ans


if __name__ == '__main__':
    import server_data.profit as profit_info
    import os
    username = os.getenv('pp_user')
    pw = os.getenv('pp_password')
    auth_data = (username, pw)

    ###
    gs = GraphSearch(server=profit_info.test_server, auth_data=auth_data)

    import datetime
    id1 = 'http://id1'
    # yesterday = (datetime.datetime.utcnow() - datetime.timedelta(days=1))
    # text1 = 'Dogs Euro European Central Bank whatever else 2'
    # cpts = gs.extract_and_update(
    #     id_=id1, title='title1', author='me',
    #     date=yesterday, text=text1
    # )
    # id2 = 'http://id2'
    # month_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=30))
    # text2 = 'Prior America Meat'
    # cpts = gs.extract_and_update(
    #     id_=id2, title='title2', author='me',
    #     date=month_ago, text=text2
    # )

    import pprint
    # search for a particular article specified by id
    r = gs.filter_id(id1)
    results = r.json()['results']
    assert len(results) == 1


    # search by author
    r = gs.filter_author('me')
    results = r.json()['results']
    print('\n\n\n Author search')
    pprint.pprint(r.json())
    assert len(results) == 2


    # search by author and sort by date
    r = gs.filter_author('me', sort={'field': 'date', 'direction': 'DESC'})  # DESC or ASC
    results = r.json()['results']
    print('\n\n\n Author search')
    pprint.pprint(r.json())
    assert len(results) == 2


    # filter by dates
    two_days_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=2))
    thirty_two_days_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=32))
    r = gs.filter_date(start=two_days_ago)
    results = r.json()['results']
    # print('\n\n\n Date Filter')
    # pprint.pprint(r.json())
    assert len(results) == 1

    r = gs.filter_date(start=thirty_two_days_ago)
    results = r.json()['results']
    assert len(results) == 2

    r = gs.filter_date(start=thirty_two_days_ago, finish=two_days_ago)
    results = r.json()['results']
    assert len(results) == 1


    # Get all possible fields
    fields = gs.get_fields().json()['searchFields']
    print([_['field'] for _ in fields])

    #filter by cpt
    uri_prefix = 'http://profit.poolparty.biz/profit_thesaurus/'
    for el in fields:
        field = el['field']
        suffix = field.split('_')[-1]
        uri = uri_prefix + suffix
        pls = pp_calls.get_pref_labels(
            uris=[uri], pid=profit_info.test_pid,
            server=profit_info.test_server, auth_data=auth_data
        )
        if pls:
            pl = pls[0]
            r = gs.filter_cpt(cpt_uri=uri)
            print('\n\n\n' + pl)
            pprint.pprint(r.json()['results'])
