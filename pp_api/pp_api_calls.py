import requests


def extract(text, pid, server):
    """
    Make extract call using project determined by pid.

    :param text: text
    :param pid: id of project
    :param server: server url
    :return: response object
    """
    data = {
        'text': text,
        'projectId': pid,
        'language': 'en',
        'numberOfTerms': 1000,
        'numberOfConcepts': 1000
    }
    r = requests.post(server + 'extractor/api/extract',
                      auth=('revenkoa', 'revenkpp'),
                      data=data)
    assert r.status_code == 200
    return r


def get_extracted_cpts(text, pid, server):
    """
    Get extracted concepts from text using project determined by pid.

    :param text: text
    :param pid: id of project
    :param server: server url
    :return: dict: {cpt_prefLabel: cpt_uri}
    """
    r = extract(text, pid, server)
    if 'concepts' in r.json():
        return {cpt['uri']: cpt['prefLabel']
                for cpt in r.json()['concepts']}
    else:
        return dict()


def get_extracted_terms(text, pid, server):
    """
    Get extracted terms from text using project determined by pid.

    :param text: text
    :param pid: id of project
    :param server: server url
    :return: list of extracted terms
    """
    r = extract(text, pid, server)
    assert r.status_code == 200
    terms = {term['textValue']: term['frequencyInDocument']
             for term in r.json()['freeTerms']}
    return terms
