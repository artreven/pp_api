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
        'numberOfConcepts': 1000,
        'numberOfTerms': 1000,
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
    assert r.status_code == 200
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


# def get_extracted_cpts(text, pid, server):
#     """
#     Get extracted concepts from text using project determined by pid.
#
#     :param text: text
#     :param pid: id of project
#     :param server: server url
#     :return: dict: {cpt_prefLabel: cpt_uri}
#     """
#     r = extract(text, pid, server)
#     if 'concepts' in r.json():
#         return {cpt['uri']: cpt['prefLabel']
#                 for cpt in r.json()['concepts']}
#     else:
#         return dict()
#
#
# def get_extracted_terms(text, pid, server):
#     """
#     Get extracted terms from text using project determined by pid.
#
#     :param text: text
#     :param pid: id of project
#     :param server: server url
#     :return: list of extracted terms
#     """
#     r = extract(text, pid, server)
#     assert r.status_code == 200
#     terms = {term['textValue']: term['frequencyInDocument']
#              for term in r.json()['freeTerms']}
#     return terms
