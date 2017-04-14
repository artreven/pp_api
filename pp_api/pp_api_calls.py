import requests


def extract(text, pid, server, auth_data):
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
        'projectId': pid,
        'language': 'en',
        'useTransitiveBroaderConcepts': True,
        'useRelatedConcepts': True,
        'sentimentAnalysis': True
    }
    r = requests.post(server + '/extractor/api/extract',
                      auth=auth_data,
                      data=data)
    assert r.status_code == 200, print(data, '\n\n', r.status_code)
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


def get_prefLabels(uris, pid, server, auth_data):
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
    r = requests.get(server +
                     '/PoolParty/api/thesaurus/{}/concepts'.format(pid),
                     auth=auth_data,
                     params=data)
    assert r.status_code == 200
    return [x['prefLabel'] for x in r.json()]


def get_cpt_corpus_freqs(corpus_id, server, pid, auth_data):
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
    while True:
        r = requests.get(server + suffix,
                         auth=auth_data,
                         params=data)
        assert r.status_code == 200
        data['startIndex'] += 20
        results += r.json()
        if not len(r.json()):
            break
    return results


def get_cpt_path(cpt_uri, server, pid, auth_data):
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
    r = requests.get(server + suffix,
                     auth=auth_data,
                     params=data)
    assert r.status_code == 200
    broaders = [(x['uri'], x['prefLabel']) for x in r.json()[0]['conceptPath']]
    cpt_scheme = r.json()[0]['conceptScheme']
    result = [(cpt_scheme['uri'], cpt_scheme['title'])] + broaders
    return result


def get_term_coocs(term, corpus_id, server, pid, auth_data):
    suffix = '/PoolParty/api/corpusmanagement/' \
             '{pid}/results/cooccurrence/term'.format(
        pid=pid
    )
    data = {
        'corpusId': corpus_id,
        'term': term,
        'startIndex': 0
    }
    results = []
    while True:
        r = requests.get(server + suffix,
                         auth=auth_data,
                         params=data)
        assert r.status_code == 200
        data['startIndex'] += 20
        results += r.json()
        if not len(r.json()):
            break
    return results


if __name__ == '__main__':
    import server_data.custom_apps as server_info
    r = extract('dummy text', server_info.pid,
                server_info.server, server_info.auth_data)
    print(r.status_code)
    print(r.json())
