import logging
import unittest

from decouple import config

from pp_api import GraphSearch

log = logging.getLogger(__name__)

server = config('PP_SERVER')
auth_data = (config('GRAPHSEARCH_USER'), config('GRAPHSEARCH_PASS'))
search_space_id = config('GRAPHSEARCH_SEARCH_SPACE_ID')

graph_search = GraphSearch(server=server, auth_data=auth_data)


class TestSearch(unittest.TestCase):
    def test_search_without_filters_response_OK(self):
        response = graph_search.search(search_space_id=search_space_id)
        self.assertEqual(200, response.status_code)

    def test_search_with_filter_fulltext_response_OK(self):
        search_filter = graph_search.filter_full_text('wall street')
        response = graph_search.search(search_filters=search_filter, search_space_id=search_space_id)

        self.assertEqual(200, response.status_code)

    def test_search_with_filter_cpt_response_OK(self):
        search_filter = graph_search.filter_cpt('http://profit.poolparty.biz/profit_thesaurus/2084')
        response = graph_search.search(search_filters=search_filter, search_space_id=search_space_id)

        self.assertEqual(200, response.status_code)


if __name__ == '__main__':
    unittest.main()
