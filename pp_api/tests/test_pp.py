import os

from pp_api import *
import pp_api.server_data.custom_apps as custom

class TestPP():
    def setUp(self):
        this_dir = os.path.dirname(__file__)
        self.data_folder = os.path.join(this_dir, 'data')
        auth_data = tuple(map(os.environ.get, ['pp_user', 'pp_password']))
        self.extract_args = {
            'server': custom.server,
            'auth_data': auth_data,
            'sparql_endpoint': custom.sparql_endpoint,
            'pid': custom.chebi_pid
        }

    def do_extract(self, text_path):
        r = extract_from_file(
            text_path, **self.extract_args
        )
        terms = get_terms_from_response(r)
        assert(terms)

    def test_sigma_pi(self):
        path = os.path.join(self.data_folder, 'question_1727.txt')
        self.do_extract(path)
