import sys

import requests


def extract(text, pid, server, auth_data=None, session=None, **kwargs):
    """
    Make extract call using project determined by pid.

    :param text: text
    :param pid: id of project
    :param server: server url
    :return: response object
    """
    data = {
        'numberOfConcepts': 100000,
        'numberOfTerms': 100000,
        'text': text,
        #'file': 'file',
        'projectId': pid,
        'language': 'en',
        'useTransitiveBroaderConcepts': True,
        'useRelatedConcepts': True,
        'sentimentAnalysis': True
    }
    data.update(kwargs)
    if session is None:
        assert auth_data is not None
        r = requests.request(
            'POST', server + '/extractor/api/extract',
            auth=auth_data,
            data=data,
            files={'file': ('.txt', text)}
        )
    else:
        if auth_data is not None:
            r = session.post(
                server + '/extractor/api/extract',
                auth=auth_data,
                data=data,
                files={'file': ('.txt', text)}
            )
        else:
            r = session.post(
                server + '/extractor/api/extract',
                data=data,
                files={'file': ('.txt', text)}
            )
    r.raise_for_status()
    return r


def get_cpts_from_response(r):
    attributes = ['prefLabel', 'frequencyInDocument', 'uri',
                  'transitiveBroaderConcepts', 'relatedConcepts']

    extr_cpts = []
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



def get_terms_from_response(r):
    attributes = ['textValue', 'frequencyInDocument', 'score']
    extr_terms = []
    term_container = r.json()

    found = False
    for term_key_word in ['freeTerms', 'extractedTerms']:
        if term_key_word in term_container:
            found = True
            break
        if not 'document' in term_container:
            found = False
            break
        if term_key_word in term_container['document']:
            term_container = term_container['document']
            found = True
            break

    assert found, extr_terms

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

    :param text: text
    :param pid: id of project
    :param server: server url
    :return: response object
    """
    data = {
        'concepts': uris,
        'projectId': pid,
        'language': 'en',
    }

    if session is None:
        assert auth_data is not None
        r = requests.get(
            server + '/PoolParty/api/thesaurus/{}/concepts'.format(pid),
            auth=auth_data,
            params=data
        )
    else:
        if auth_data is not None:
            r = session.get(
                server + '/PoolParty/api/thesaurus/{}/concepts'.format(pid),
                auth=auth_data,
                params=data
            )
        else:
            r = session.get(
                server + '/PoolParty/api/thesaurus/{}/concepts'.format(pid),
                params=data
            )
    r.raise_for_status()
    return [x['prefLabel'] for x in r.json()]


def get_cpt_corpus_freqs(corpus_id, server, pid, auth_data=None, session=None):
    """
    Make call to PP to extract frequencies of concepts in a corpus.

    :param corpus_id: corpus id
    :param pid: id of project
    :param server: server url
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

    if session is None:
        assert auth_data is not None
        while True:
            r = requests.get(server + suffix,
                             auth=auth_data,
                             params=data)
            r.raise_for_status()
            data['startIndex'] += 20
            results += r.json()
            if not len(r.json()):
                break
    else:
        if auth_data is not None:
            while True:
                r = session.get(server + suffix,
                                auth=auth_data,
                                params=data)
                r.raise_for_status()
                data['startIndex'] += 20
                results += r.json()
                if not len(r.json()):
                    break
        else:
            while True:
                r = session.get(server + suffix,
                                params=data)
                r.raise_for_status()
                data['startIndex'] += 20
                results += r.json()
                if not len(r.json()):
                    break

    return results


def get_cpt_path(cpt_uri, server, pid, auth_data=None, session=None):
    """
    Make call to PP to extract path of concept.

    :param corpus_id: corpus id
    :param pid: id of project
    :param server: server url
    :return: response object
    """
    data = {
        'concept': cpt_uri
    }
    suffix = '/PoolParty/api/thesaurus/{pid}/getPaths'.format(
        pid=pid
    )
    if session is None:
        assert auth_data is not None
        r = requests.get(server + suffix,
                         auth=auth_data,
                         params=data)
    else:
        r = session.get(server + suffix,
                        params=data)
    r.raise_for_status()
    broaders = [(x['uri'], x['prefLabel']) for x in r.json()[0]['conceptPath']]
    cpt_scheme = r.json()[0]['conceptScheme']
    result = [(cpt_scheme['uri'], cpt_scheme['title'])] + broaders
    return result


def get_term_coocs(term_str, corpus_id, server, pid,
                   auth_data=None, session=None):
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

    if session is None:
        assert auth_data is not None
        session = requests.session()
    if auth_data is not None:
        session.auth = auth_data
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

    if session is None:
        assert auth_data is not None
        while True:
            r = requests.get(server + suffix,
                             auth=auth_data,
                             params=data)
            r.raise_for_status()
            data['startIndex'] += 20
            print(data['startIndex'])
            results += r.json()
            if not len(r.json()):
                break
    else:
        if auth_data is not None:
            while True:
                r = session.get(server + suffix,
                                auth=auth_data,
                                params=data)
                r.raise_for_status()
                data['startIndex'] += 20
                results += r.json()
                if not len(r.json()):
                    break
        else:
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

    if session is None:
        assert auth_data is not None
        while True:
            r = requests.get(server + suffix,
                             auth=auth_data,
                             params=data)
            r.raise_for_status()
            data['startIndex'] += 20
            results += r.json()
            if not len(r.json()):
                break
    else:
        if auth_data is not None:
            while True:
                r = session.get(server + suffix,
                                auth=auth_data,
                                params=data)
                r.raise_for_status()
                data['startIndex'] += 20
                results += r.json()
                if not len(r.json()):
                    break
        else:
            while True:
                r = session.get(server + suffix,
                                params=data)
                r.raise_for_status()
                data['startIndex'] += 20
                results += r.json()
                if not len(r.json()):
                    break

    return results


if __name__ == '__main__':
    import server_data.custom_apps as server_info
    # import server_data.preview as server_info
    r = get_corpus_documents(
        server_info.corpus_id, server_info.pid,
        server_info.server, auth_data=server_info.auth_data
    )
    print(r)
