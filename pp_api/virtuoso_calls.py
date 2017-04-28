import requests
import numpy as np
import rdflib


def get_corpus_zscores(term_uris, cooc_corpus_graph):
    """
    Get zscores for term-term cooccurrences.

    :param term_uris: list: uris of 2 terms
    :param cooc_corpus_graph: graph of corpus coocs
    :return: float [0, 1]: similarity score := zscore/max(zscore)
    """
    def similarity(term1_uri, term2_uri):
        if term1_uri == term2_uri:
            return 1
        elif (term1_uri, term2_uri) in sim_matrix:
            return sim_matrix[(term1_uri, term2_uri)]
        elif (term2_uri, term1_uri) in sim_matrix:
            return sim_matrix[(term2_uri, term1_uri)]
        else:
            return 0

    query_text = """
select ?uri1 ?uri2 ?score where {{
  ?uri1 <http://schema.semantic-web.at/ppcm/2013/5/hasTermCooccurrence> ?co.
  ?co <http://schema.semantic-web.at/ppcm/2013/5/cooccurringExtractedTerm> ?uri2.
  ?co <http://schema.semantic-web.at/ppcm/2013/5/zscore> ?score.
}}"""
    params = {
        'default-graph-uri': '{}'.format(cooc_corpus_graph),
        'query': query_text,
        'format': 'json',
    }
    r = requests.get('https://aligned-virtuoso.poolparty.biz/sparql',
                     params=params)
    assert r.status_code == 200
    sim_matrix = dict()
    c1 = 0
    c2 = 0
    for binding in r.json()['results']['bindings']:
        uri1 = binding['uri1']['value']
        uri2 = binding['uri2']['value']
        if uri1 in term_uris and uri2 in term_uris:
            sim_matrix[(uri1, uri2)] = np.log2(float(binding['score']['value']))
    max_score = max(sim_matrix.values())
    for k in sim_matrix:
        sim_matrix[k] /= max_score
    return similarity


def get_pp_terms(corpus_graph_terms, CRS_threshold=5):
    """
    Load all terms with combinedRelevanceScore is greater than CRS_threshold
    from the graph corpus_graph_terms.

    :param corpus_graph_terms: uri of the graph
    :param CRS_threshold: min combinedRelevanceScore of term to be returned
    :return:
    """
    params = {
        'default-graph-uri': '{}'.format(corpus_graph_terms),
        'query': """
select ?termUri ?name ?score where {{
  ?termUri <http://schema.semantic-web.at/ppcm/2013/5/combinedRelevanceScore> ?score .
  ?termUri <http://schema.semantic-web.at/ppcm/2013/5/name> ?name .
  filter (?score > {})
}} order by desc(?score)""".format(CRS_threshold),
        'format': 'json',
    }
    r = requests.get('https://aligned-virtuoso.poolparty.biz/sparql',
                     params=params)
    top_terms_scores = dict()
    top_terms_uris = dict()
    for new_term in r.json()['results']['bindings']:
        name = new_term['name']['value']
        score = float(new_term['score']['value'])
        term_uri = new_term['termUri']['value']
        top_terms_scores[name] = score
        top_terms_uris[name] = term_uri
    return top_terms_scores, top_terms_uris


all_data_q = """
select distinct * where {{
  ?s ?p ?o
}}
"""


q_get_doc_text_by_doc_id = """
select distinct * where {{
    <{doc_id}> <http://schema.semantic-web.at/ppcm/2013/5/htmlText> ?o
}}
"""


def query_sparql_endpoint(sparql_endpoint, graph_name,
                          query=all_data_q):
    graph = rdflib.Graph('SPARQLStore', identifier=graph_name)
    graph.open(sparql_endpoint)
    rs = graph.query(query)
    return rs


def get_ridfs(sparql_endpoint, termsgraph):
    q_term_scores = """
    select distinct ?lemma ?ridf ?crs where {{
        ?s <http://schema.semantic-web.at/ppcm/2013/5/textValue> ?lemma .
        ?s <http://schema.semantic-web.at/ppcm/2013/5/ridfTermScore> ?ridf .
        ?s <http://schema.semantic-web.at/ppcm/2013/5/combinedRelevanceScore> ?crs .
    }}
    """
    rs = query_sparql_endpoint(sparql_endpoint, termsgraph, q_term_scores)
    results = dict()
    for r in rs:
        results[str(r[0])] = float(r[2])
    return results


def query_cpt_cooc_scores(sparql_endpoint, cpt_cooc_graph):
    q_cooc_score = """
select distinct ?cpt1 ?cpt2 ?score where {{
  ?cpt1 <http://schema.semantic-web.at/ppcm/2013/5/hasConceptCooccurrence> ?o .
  ?o <http://schema.semantic-web.at/ppcm/2013/5/cooccurringExtractedConcept> ?cpt2 .
  ?o <http://schema.semantic-web.at/ppcm/2013/5/score> ?score
}}
"""
    rs = query_sparql_endpoint(sparql_endpoint, cpt_cooc_graph, q_cooc_score)
    dist_mx = dict()
    for r in rs:
        cpt1 = str(r[0])
        cpt2 = str(r[1])
        if cpt1 in dist_mx:
            dist_mx[cpt1][cpt2] = float(r[2])
        else:
            dist_mx[cpt1] = {cpt2: float(r[2])}
        if cpt2 in dist_mx:
            dist_mx[cpt2][cpt1] = float(r[2])
        else:
            dist_mx[cpt2] = {cpt1: float(r[2])}
    return dist_mx


if __name__ == '__main__':
    pass
