import requests


def extract(text, pid, server, auth_data=None, session=None):
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
        # 'file': 'file',
        'projectId': pid,
        'language': 'en',
        'useTransitiveBroaderConcepts': True,
        'useRelatedConcepts': True,
        'sentimentAnalysis': True
    }
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
    extr_cpts = []
    if 'concepts' in r.json():
        attributes = ['prefLabel', 'frequencyInDocument', 'uri',
                      'transitiveBroaderConcepts', 'relatedConcepts']
        for cpt_json in r.json()['concepts']:
            cpt = dict()
            for attr in attributes:
                if attr in cpt_json:
                    cpt[attr] = cpt_json[attr]
                else:
                    cpt[attr] = []
            extr_cpts.append(cpt)
        return extr_cpts
    else:
        return extr_cpts


def get_terms_from_response(r):
    extr_terms = []
    if 'extractedTerms' in r.json():
        attributes = ['textValue', 'frequencyInDocument', 'score']
        for term_json in r.json()['extractedTerms']:
            term = dict()
            for attr in attributes:
                if attr in term_json:
                    term[attr] = term_json[attr]
                else:
                    term[attr] = []
            extr_terms.append(term)
        return extr_terms
    else:
        return extr_terms


def get_sentiment_from_response(r):
    return r.json()["sentiments"][0]["score"]


def get_prefLabels(uris, pid, server, auth_data=None, session=None):
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

