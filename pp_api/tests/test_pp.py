import os

from pp_api import *
import pp_api.server_data.custom_apps as custom

class TestPP():
    def setUp(self):
        this_dir = os.path.dirname(__file__)
        self.data_folder = os.path.join(this_dir, 'data')
        auth_data = tuple(map(os.environ.get, ['pp_user', 'pp_password']))
        assert auth_data[0] and auth_data[1]
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
        # print(r.json())
        #assert(terms)

    def test_sigma_pi(self):
        path = os.path.join(self.data_folder, 'question_1727.txt')
        self.do_extract(path)

    def test_illegal_char_sentiment(self):
        path = os.path.join(self.data_folder, 'question_2189.txt')
        self.do_extract(path)

    def test_small_question(self):
        path = os.path.join(self.data_folder, 'question_921.txt')
        self.do_extract(path)

    def test_shadow_cpts_extraction(self):
        text_path = os.path.join(self.data_folder, 'question_1727.txt')
        self.extract_args.update({
            'shadow_cpts_corpus_id': custom.chebi_corpus_id
        })
        print(self.extract_args)
        with open(text_path) as f:
            text = f.read()
        scpts, r = extract_shadow_cpts(
            text,
            **self.extract_args
        )
        assert hasattr(scpts, '__len__')
        assert len(scpts) > 0
