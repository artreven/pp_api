import requests
from requests.exceptions import HTTPError
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import tempfile
import logging
import traceback
from time import time

from pp_api import utils as u

root_logger = logging.getLogger('root')


class PoolParty:
    def __init__(self, server, auth_data=None, session=None, max_retries=None):
        self.auth_data = auth_data
        self.server = server
        self.session = u.get_session(session, auth_data)
        if max_retries is not None:
            retries = Retry(total=max_retries,
                            backoff_factor=0.3,
                            status_forcelist=[500, 502, 503, 504])
            self.session.mount(self.server, HTTPAdapter(max_retries=retries))

    def extract(self, text, pid, lang='en', **kwargs):
        """
        Make extract call using project determined by pid.

        :param auth_data:
        :param session:
        :param text: text
        :param pid: id of project
        :param server: server url
        :param lang: language
        :return: response object
        """
        tmp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+b')
        tmp_file.write(str(text).encode('utf8'))
        tmp_file.seek(0)
        return self.extract_from_file(tmp_file, pid, lang=lang, **kwargs)

    def extract_from_file(self, file, pid, mb_time_factor=3, lang='en',
                          **kwargs):
        """
        Make extract call using project determined by pid.

        :param text: text
        :param pid: id of project
        :return: response object
        """
        data = {
            'numberOfConcepts': 100000,
            'numberOfTerms': 100000,
            'projectId': pid,
            'language': lang,
            'useTransitiveBroaderConcepts': True,
            'useRelatedConcepts': True,
            # 'sentimentAnalysis': True,
            'filterNestedConcepts': True,
            'showMatchingPosition': True,
            'showMatchingDetails': True
        }
        data.update(kwargs)
        target_url = self.server + '/extractor/api/extract'
        start = time()
        try:
            if not hasattr(file, 'read'):
                file = open(file, 'rb')
            file_text = file.read()
            # Findout filesize
            file.seek(0, 2)  # Go to end of file
            f_size_mb = file.tell() / (1024 * 1024)
            file.seek(0)  # Go to start of file
            r = self.session.post(
                target_url,
                data=data,
                files={'file': file},
                timeout=(3.05, int(27 * mb_time_factor * (1 + f_size_mb)))
            )
        except Exception as e:
            root_logger.error(traceback.format_exc())
        finally:
            file.close()
        root_logger.debug('call took {:0.3f}'.format(time() - start))
        if not 'r' in locals():
            return None
        try:
            r.raise_for_status()
        except HTTPError as e:
            logging.error(data)
            logging.error(file_text)
            logging.error(r.text)
            raise e
        return r

    @staticmethod
    def get_cpts_from_response(r):
        attributes = ['prefLabel', 'frequencyInDocument', 'uri',
                      'transitiveBroaderConcepts', 'relatedConcepts']

        extr_cpts = []
        if r is None:
            return extr_cpts
        concept_container = r.json()

        if not 'concepts' in concept_container:
            if not 'document' in concept_container:
                return extr_cpts
            if not 'concepts' in concept_container['document']:
                # no mention of concepts either in the json directly or document inside
                return extr_cpts
            else:
                # concepts are mentioned inside 'document'
                concept_container = concept_container['document']

        for cpt_json in concept_container['concepts']:
            cpt = dict()
            for attr in attributes:
                if attr in cpt_json:
                    cpt[attr] = cpt_json[attr]
                else:
                    cpt[attr] = []
            if 'matchingLabels' in cpt_json:
                cpt_matchings = []
                ms = sum([x['matchedTexts'] for x in cpt_json['matchingLabels']],
                         [])
                for m in ms:
                    cpt_matching = {
                        'text': m['matchedText'],
                        'frequency': m['frequency'],
                        'positions': [(x['beginningIndex'], x['endIndex'])
                                      for x in m['positions']]
                    }
                    cpt_matchings.append(cpt_matching)
                cpt['matchings'] = cpt_matchings
            extr_cpts.append(cpt)

        return extr_cpts

    def extract_shadow_cpts(self, text, shadow_cpts_corpus_id, pid, **kwargs):
        r = self.extract(
            text, pid, shadowConceptCorpusId=shadow_cpts_corpus_id, **kwargs
        )

        attributes = ['prefLabel', 'uri',
                      'transitiveBroaderConcepts', 'relatedConcepts',
                      'corporaScore']

        shadow_cpts = []
        if r is None:
            return shadow_cpts
        concept_container = r.json()

        if not 'shadowConcepts' in concept_container:
            if not 'document' in concept_container:
                return shadow_cpts
            if not 'shadowConcepts' in concept_container['document']:
                # no mention of concepts either in the json directly or document inside
                return shadow_cpts
            else:
                # concepts are mentioned inside 'document'
                concept_container = concept_container['document']

        for cpt_json in concept_container['shadowConcepts']:
            cpt = dict()
            for attr in attributes:
                if attr in cpt_json:
                    cpt[attr] = cpt_json[attr]
                else:
                    cpt[attr] = []
            shadow_cpts.append(cpt)

        return shadow_cpts, r

    @staticmethod
    def get_terms_from_response(r):
        attributes = ['textValue', 'frequencyInDocument', 'score']
        extr_terms = []
        if r is None:
            return extr_terms
        term_container = r.json()

        found = False
        for term_key_word in ['freeTerms', 'extractedTerms']:
            if term_key_word in term_container:
                found = True
                break
            elif 'document' in term_container and term_key_word in \
                    term_container['document']:
                term_container = term_container['document']
                found = True
                break

        if not found:
            root_logger.warning("No terms found in this document!")
            return extr_terms

        assert found, [extr_terms, list(term_container.keys()), r.json()]

        for term_json in term_container[term_key_word]:
            term = dict()
            for attr in attributes:
                if attr in term_json:
                    term[attr] = term_json[attr]
                else:
                    term[attr] = []
            extr_terms.append(term)

        return extr_terms

    @staticmethod
    def get_sentiment_from_response(r):
        return r.json()["sentiments"][0]["score"]

    def get_pref_labels(self, uris, pid):
        """
        Get prefLabels (in English) of all concepts specified by uris.

        :param uris:
        :param pid: id of project
        :return: response object
        """
        data = {
            'concepts': uris,
            'projectId': pid,
            'language': 'en',
        }
        r = self.session.get(
            self.server + '/PoolParty/api/thesaurus/{}/concepts'.format(pid),
            params=data
        )
        r.raise_for_status()
        return [x['prefLabel'] for x in r.json()]

    def get_cpt_corpus_freqs(self, corpus_id, pid):
        """
        Make call to PP to extract frequencies of concepts in a corpus.

        :param corpus_id: corpus id
        :param pid: id of project
        :return: response object
        """
        data = {
            'corpusId': corpus_id,
            'startIndex': 0
        }
        suffix = '/PoolParty/api/corpusmanagement/{pid}/results/concepts'.format(
            pid=pid
        )
        results = []
        while True:
            r = self.session.get(self.server + suffix, params=data)
            r.raise_for_status()
            data['startIndex'] += 20
            results += r.json()
            if not len(r.json()):
                break
        return results

    def get_cpt_path(self, cpt_uri, pid):
        """
        Make call to PP to extract path of concept.

        :param cpt_uri:
        :param pid: id of project
        :return: list: [(uri, label)] of cpt scheme and broaders
        """

        cpt_uri = str(cpt_uri)
        data = {
            'concept': cpt_uri
        }
        suffix = '/PoolParty/api/thesaurus/{pid}/getPaths'.format(
            pid=pid
        )
        r = self.session.get(self.server + suffix, params=data)
        r.raise_for_status()
        broaders = [(x['uri'], x['prefLabel']) for x in
                    r.json()[0]['conceptPath']]
        cpt_scheme = r.json()[0]['conceptScheme']
        result = [(cpt_scheme['uri'], cpt_scheme['title'])] + broaders
        return result

    def get_term_coocs(self, term_str, corpus_id, pid):
        suffix = '/PoolParty/api/corpusmanagement/' \
                 '{pid}/results/cooccurrence/term'.format(
            pid=pid
        )
        data = {
            'corpusId': corpus_id,
            'term': term_str,
            'startIndex': 0,
            'limit': 2 ** 15,  # int(sys.maxsize)
        }
        results = []

        while True:
            r = self.session.get(self.server + suffix,
                            params=data)
            r.raise_for_status()
            results += r.json()
            if len(r.json()) == 20:
                data['startIndex'] += len(r.json())
                if not len(r.json()):
                    break
            else:
                break

        return results

    def get_projects(self):
        suffix = '/PoolParty/api/projects'
        r = self.session.get(self.server + suffix)
        r.raise_for_status()
        result = r.json()
        return result

    def get_corpora(self, pid):
        suffix = '/PoolParty/api/corpusmanagement/{pid}/corpora'.format(pid=pid)
        r = self.session.get(self.server + suffix)
        r.raise_for_status()
        result = r.json()['jsonCorpusList']
        return result

    def get_corpus_documents(self, corpus_id, pid):
        suffix = '/PoolParty/api/corpusmanagement/{pid}/documents'.format(
            pid=pid)
        data = {
            'corpusId': corpus_id,
            'includeContent': True
        }
        r = self.session.get(self.server + suffix, params=data)
        r.raise_for_status()
        result = r.json()
        return result

    def get_document_terms(self, doc_id, corpus_id, pid):
        suffix = '/PoolParty/api/corpusmanagement/{pid}/documents/{docid}'.format(
            pid=pid, docid=doc_id
        )
        data = {
            'corpusId': corpus_id
        }
        r = self.session.get(self.server + suffix, params=data)
        r.raise_for_status()
        result = r.json()
        return result

    def get_allterms_scores(self, corpus_id, pid):
        suffix = '/PoolParty/api/corpusmanagement/{pid}/results/extractedterms'.format(
            pid=pid
        )
        data = {
            'corpusId': corpus_id,
            'startIndex': 0
        }
        results = []
        while True:
            r = self.session.get(self.server + suffix,
                                 params=data)
            r.raise_for_status()
            data['startIndex'] += 20
            results += r.json()
            if not len(r.json()):
                break
        return results

    def get_terms_stats(self, corpus_id, pid):
        suffix = '/PoolParty/api/corpusmanagement/{pid}/results/extractedterms'.format(
            pid=pid
        )
        data = {
            'corpusId': corpus_id,
            'startIndex': 0
        }
        results = []
        while True:
            r = self.session.get(self.server + suffix,
                                 params=data)
            r.raise_for_status()
            data['startIndex'] += 20
            results += r.json()
            if not len(r.json()):
                break
        return results

    def export_project(self, pid):
        suffix = '/PoolParty/api/projects/{pid}/export'.format(
            pid=pid
        )
        rdf_format = 'N3'
        data = {
            'format': rdf_format,
            'exportModules': ['concepts']
        }
        r = self.session.get(self.server + suffix, params=data)
        r.raise_for_status()
        return r.content

    def get_autocomplete(self, query_str, pid, lang='en'):
        suffix = '/extractor/api/suggest'
        data = {
            'projectId': pid,
            'searchString': query_str,
            'language': lang
        }
        r = self.session.get(self.server + suffix, params=data)
        r.raise_for_status()
        if r.json()['suggestedConcepts']:
            ans = [(x['prefLabel'], x['uri'])
                   for x in r.json()['suggestedConcepts']]
        else:
            ans = []
        return ans

    def get_onto(self, uri):
        suffix = '/PoolParty/api/schema/ontology'
        data = {
            'uri': uri
        }
        r = self.session.get(self.server + suffix, params=data)
        r.raise_for_status()
        ans = r.json()
        return ans

    def get_history(self, pid, from_=None):
        """

        :param pid: project
        :param from_: datetime instance or None
        :return:
        """
        suffix = '/PoolParty/api/history/{pid}'.format(
            pid=pid
        )
        data = dict()
        if from_ is not None:
            data.update({
                'fromTime': from_.strftime('%Y-%m-%dT%H:%M:%S')
            })
        r = self.session.get(self.server + suffix, params=data)
        r.raise_for_status()
        return r.json()

    def get_schemes(self, pid):
        suffix = '/PoolParty/api/thesaurus/{project}/schemes'.format(
            project=pid
        )
        r = self.session.get(self.server + suffix)
        r.raise_for_status()
        ans = r.json()
        return ans

    def add_new_concept(self, pid, pref_label, parent=None):
        suffix = '/PoolParty/api/thesaurus/{project}/createConcept'.format(
            project=pid
        )
        data = {
            'prefLabel': pref_label,
            'parent': (parent if parent is not None else
                       self.get_schemes(pid)[0]['uri'])
        }
        r = self.session.post(self.server + suffix, data=data)
        r.raise_for_status()
        ans = r.json()
        return ans

    def add_label(self, pid, uri, label_value,
                  label_type='skos:altLabel', lang=None):
        suffix = '/PoolParty/api/thesaurus/{project}/addLiteral'.format(
            project=pid
        )
        data = {
            'concept': uri,
            'label': label_value,
            'property': label_type,
            'language': lang
        }
        r = self.session.post(self.server + suffix, data=data)
        r.raise_for_status()
        return r

    def add_relation(self, pid, source_uri, target_uri,
                     relation_type='skos:narrower'):
        suffix = '/PoolParty/api/thesaurus/{project}/addRelation'.format(
            project=pid
        )
        data = {
            'sourceConcept': source_uri,
            'targetConcept': target_uri,
            'property': relation_type,
        }
        r = self.session.post(self.server + suffix, data=data)
        r.raise_for_status()
        return r

    def add_narrower(self, pid, broader_uri, narrower_uri):
        return self.add_relation(
            pid=pid, source_uri=broader_uri, target_uri=narrower_uri,
            relation_type='skos:narrower'
        )

    def add_related(self, pid, source_uri, target_uri):
        return self.add_relation(
            pid=pid, source_uri=source_uri, target_uri=target_uri,
            relation_type='skos:related'
        )

    def get_cpt_narrowers(self, pid, cpt_uri, transitive=True, lang=None):
        suffix = '/PoolParty/api/thesaurus/{project}/narrowers'.format(
            project=pid
        )
        data = {
            'concept': cpt_uri,
            'properties': 'all',
            'transitive': transitive,
        }
        if lang is not None:
            data['language'] = lang
        r = self.session.get(self.server + suffix, params=data)
        r.raise_for_status()
        return r



########################
########################
########################


def extract(text, pid, server, auth_data=None, session=None, max_retries=None,
            **kwargs):
    """
    Make extract call using project determined by pid.

    :param auth_data: 
    :param session: 
    :param text: text
    :param pid: id of project
    :param server: server url
    :return: response object
    """
    tmp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+b')
    tmp_file.write(str(text).encode('utf8'))
    tmp_file.seek(0)
    return extract_from_file(tmp_file, pid, server, auth_data, session,
                             max_retries,
                             **kwargs)


def extract_from_file(file, pid, server, auth_data=None, session=None,
                      max_retries=None, mb_time_factor=3,**kwargs):
    """
    Make extract call using project determined by pid.

    :param auth_data:
    :param session:
    :param text: text
    :param pid: id of project
    :param server: server url
    :return: response object
    """
    root_logger.warning(
        'Please, consider switching to using PoolParty object for making calls to PoolParty.')
    data = {
        'numberOfConcepts': 100000,
        'numberOfTerms': 100000,
        'projectId': pid,
        'language': 'en',
        'useTransitiveBroaderConcepts': True,
        'useRelatedConcepts': True,
        # 'sentimentAnalysis': True,
        'filterNestedConcepts': True
    }
    data.update(kwargs)
    session = u.get_session(session, auth_data)
    target_url = server + '/extractor/api/extract'
    start = time()
    try:
        if not hasattr(file, 'read'):
            file = open(file, 'rb')
        # Findout filesize
        file.seek(0, 2) # Go to end of file
        f_size_mb = file.tell() / (1024 * 1024)
        file.seek(0) # Go to start of file
        if max_retries is not None:
            retries = Retry(total=max_retries,
                            backoff_factor=0.3,
                            status_forcelist=[500, 502, 503, 504])
            session.mount(server, HTTPAdapter(max_retries=retries))
        r = session.post(
            target_url,
            data=data,
            files={'file': file},
            timeout=(3.05, int(27 * mb_time_factor*(1 + f_size_mb )))
        )
    except Exception as e:
        root_logger.error(traceback.format_exc())
    finally:
        file.close()
    root_logger.debug('call took {:0.3f}'.format(time() - start))
    if not 'r' in locals():
        return None
    try:
        r.raise_for_status()
    except HTTPError as e:
        logging.error(r.text)
        raise e
    return r


def get_cpts_from_response(r):
    attributes = ['prefLabel', 'frequencyInDocument', 'uri',
                  'transitiveBroaderConcepts', 'relatedConcepts']

    extr_cpts = []
    if r is None:
        return extr_cpts
    concept_container = r.json()

    if not 'concepts' in concept_container:
        if not 'document' in concept_container:
            return extr_cpts
        if not 'concepts' in concept_container['document']:
            #no mention of concepts either in the json directly or document inside
            return extr_cpts
        else:
            #concepts are mentioned inside 'document'
            concept_container = concept_container['document']

    for cpt_json in concept_container['concepts']:
        cpt = dict()
        for attr in attributes:
            if attr in cpt_json:
                cpt[attr] = cpt_json[attr]
            else:
                cpt[attr] = []
        extr_cpts.append(cpt)

    return extr_cpts


def extract_shadow_cpts(text, shadow_cpts_corpus_id, pid, server,
                        auth_data=None, session=None, max_retries=None,
                        **kwargs):
    root_logger.warning(
        'Please, consider switching to using PoolParty object for making calls to PoolParty.')
    r = extract(text, pid, server,
                auth_data, session, max_retries,
                shadowConceptCorpusId=shadow_cpts_corpus_id,
                **kwargs)

    attributes = ['prefLabel', 'uri',
                  'transitiveBroaderConcepts', 'relatedConcepts', 'corporaScore']

    shadow_cpts = []
    if r is None:
        return shadow_cpts
    concept_container = r.json()

    if not 'shadowConcepts' in concept_container:
        if not 'document' in concept_container:
            return shadow_cpts
        if not 'shadowConcepts' in concept_container['document']:
            #no mention of concepts either in the json directly or document inside
            return shadow_cpts
        else:
            #concepts are mentioned inside 'document'
            concept_container = concept_container['document']

    for cpt_json in concept_container['shadowConcepts']:
        cpt = dict()
        for attr in attributes:
            if attr in cpt_json:
                cpt[attr] = cpt_json[attr]
            else:
                cpt[attr] = []
        shadow_cpts.append(cpt)

    return shadow_cpts, r


def get_terms_from_response(r):
    attributes = ['textValue', 'frequencyInDocument', 'score']
    extr_terms = []
    if r is None:
        return extr_terms
    term_container = r.json()

    found = False
    for term_key_word in ['freeTerms', 'extractedTerms']:
        if term_key_word in term_container:
            found = True
            break
        elif 'document' in term_container and term_key_word in term_container['document']:
            term_container = term_container['document']
            found = True
            break

    if not found:
        root_logger.warning("No terms found in this document!")
        return extr_terms

    assert found, [extr_terms, list(term_container.keys()), r.json()]

    for term_json in term_container[term_key_word]:
        term = dict()
        for attr in attributes:
            if attr in term_json:
                term[attr] = term_json[attr]
            else:
                term[attr] = []
        extr_terms.append(term)

    return extr_terms


def get_sentiment_from_response(r):
    return r.json()["sentiments"][0]["score"]


def get_pref_labels(uris, pid, server, auth_data=None, session=None):
    """
    Make extract call using project determined by pid.

    :param uris: 
    :param auth_data: 
    :param session: 
    :param pid: id of project
    :param server: server url
    :return: response object
    """
    root_logger.warning(
        'Please, consider switching to using PoolParty object for making calls to PoolParty.')
    data = {
        'concepts': uris,
        'projectId': pid,
        'language': 'en',
    }
    session = u.get_session(session, auth_data)
    r = session.get(
        server + '/PoolParty/api/thesaurus/{}/concepts'.format(pid),
        params=data
    )
    r.raise_for_status()
    return [x['prefLabel'] for x in r.json()]


def get_cpt_corpus_freqs(corpus_id, server, pid, auth_data=None, session=None):
    """
    Make call to PP to extract frequencies of concepts in a corpus.

    :param auth_data: 
    :param session: 
    :param corpus_id: corpus id
    :param pid: id of project
    :param server: server url
    :return: response object
    """
    root_logger.warning(
        'Please, consider switching to using PoolParty object for making calls to PoolParty.')
    data = {
        'corpusId': corpus_id,
        'startIndex': 0
    }
    suffix = '/PoolParty/api/corpusmanagement/{pid}/results/concepts'.format(
        pid=pid
    )
    results = []
    session = u.get_session(session, auth_data)
    while True:
        r = session.get(server + suffix, params=data)
        r.raise_for_status()
        data['startIndex'] += 20
        results += r.json()
        if not len(r.json()):
            break
    return results


def get_cpt_path(cpt_uri, server, pid, auth_data=None, session=None):
    """
    Make call to PP to extract path of concept.

    :param cpt_uri: 
    :param auth_data: 
    :param session: 
    :param pid: id of project
    :param server: server url
    :return: response object
    """
    root_logger.warning(
        'Please, consider switching to using PoolParty object for making calls to PoolParty.')
    cpt_uri = str(cpt_uri)
    data = {
        'concept': cpt_uri
    }
    suffix = '/PoolParty/api/thesaurus/{pid}/getPaths'.format(
        pid=pid
    )
    session = u.get_session(session, auth_data)
    r = session.get(server + suffix, params=data)
    r.raise_for_status()
    broaders = [(x['uri'], x['prefLabel']) for x in r.json()[0]['conceptPath']]
    cpt_scheme = r.json()[0]['conceptScheme']
    result = [(cpt_scheme['uri'], cpt_scheme['title'])] + broaders
    return result


def get_term_coocs(term_str, corpus_id, server, pid,
                   auth_data=None, session=None):
    root_logger.warning(
        'Please, consider switching to using PoolParty object for making calls to PoolParty.')
    suffix = '/PoolParty/api/corpusmanagement/' \
             '{pid}/results/cooccurrence/term'.format(
        pid=pid
    )
    data = {
        'corpusId': corpus_id,
        'term': term_str,
        'startIndex': 0,
        'limit': 2**15, #int(sys.maxsize)
    }
    results = []

    session = u.get_session(session, auth_data)
    while True:
        r = session.get(server + suffix,
                        params=data)
        r.raise_for_status()
        results += r.json()
        if len(r.json()) == 20:
            data['startIndex'] += len(r.json())
            if not len(r.json()):
                break
        else:
            break

    return results


def get_projects(server, auth_data):
    suffix = '/PoolParty/api/projects'
    r = requests.get(server + suffix, auth=auth_data)
    r.raise_for_status()
    result = r.json()
    return result


def get_corpora(server, pid, auth_data):
    suffix = '/PoolParty/api/corpusmanagement/{pid}/corpora'.format(pid=pid)
    r = requests.get(server + suffix, auth=auth_data)
    r.raise_for_status()
    result = r.json()['jsonCorpusList']
    return result


def get_corpus_documents(corpus_id, pid, server, auth_data):
    suffix = '/PoolParty/api/corpusmanagement/{pid}/documents'.format(pid=pid)
    data = {
        'corpusId': corpus_id,
        'includeContent': True
    }
    r = requests.get(server + suffix, auth=auth_data, params=data)
    r.raise_for_status()
    result = r.json()
    return result


def get_document_terms(doc_id, corpus_id, pid, server, auth_data):
    suffix = '/PoolParty/api/corpusmanagement/{pid}/documents/{docid}'.format(
        pid=pid, docid=doc_id
    )
    data = {
        'corpusId': corpus_id
    }
    r = requests.get(server + suffix, auth=auth_data, params=data)
    r.raise_for_status()
    result = r.json()
    return result


def get_allterms_scores(corpus_id, pid, server, auth_data=None, session=None):
    suffix = '/PoolParty/api/corpusmanagement/{pid}/results/extractedterms'.format(
        pid=pid
    )
    data = {
        'corpusId': corpus_id,
        'startIndex': 0
    }
    results = []
    session = u.get_session(session, auth_data)
    while True:
        r = session.get(server + suffix,
                        params=data)
        r.raise_for_status()
        data['startIndex'] += 20
        results += r.json()
        if not len(r.json()):
            break
    return results


def get_terms_stats(corpus_id, pid, server, auth_data=None, session=None):
    suffix = '/PoolParty/api/corpusmanagement/{pid}/results/extractedterms'.format(
        pid=pid
    )
    data = {
        'corpusId': corpus_id,
        'startIndex': 0
    }
    results = []
    session = u.get_session(session, auth_data)
    while True:
        r = session.get(server + suffix,
                        params=data)
        r.raise_for_status()
        data['startIndex'] += 20
        results += r.json()
        if not len(r.json()):
            break
    return results


def export_project(pid, server, auth_data=None, session=None):
    suffix = '/PoolParty/api/projects/{pid}/export'.format(
        pid=pid
    )
    rdf_format = 'N3'
    data = {
        'format': rdf_format,
        'exportModules': ['concepts']
    }
    session = u.get_session(session, auth_data)
    r = session.get(server + suffix, params=data)
    r.raise_for_status()
    return r.content


if __name__ == '__main__':
    pass

