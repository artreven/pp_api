import requests
import numpy as np
import rdflib


def get_corpus_analysis_graphs(corpus_id):
    corpusgraph_id = 'corpusgraph:' + corpus_id[7:]
    termsgraph_id = corpusgraph_id + ':extractedTerms'
    cpt_occur_graph_id = corpusgraph_id + ':conceptOccurrences'
    cooc_graph = corpusgraph_id + ':cooccurrence'
    return corpusgraph_id, termsgraph_id, cpt_occur_graph_id, cooc_graph


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
    for binding in r.json()['results']['bindings']:
        uri1 = binding['uri1']['value']
        uri2 = binding['uri2']['value']
        if uri1 in term_uris and uri2 in term_uris:
            sim_matrix[(uri1, uri2)] = np.log2(float(binding['score']['value']))
    max_score = max(sim_matrix.values())
    for k in sim_matrix:
        sim_matrix[k] /= max_score
    return similarity


def get_pp_terms(corpus_graph_terms, crs_threshold=5):
    """
    Load all terms with combinedRelevanceScore is greater than CRS_threshold
    from the graph corpus_graph_terms.

    :param corpus_graph_terms: uri of the graph
    :param crs_threshold: min combinedRelevanceScore of term to be returned
    :return:
    """
    params = {
        'default-graph-uri': '{}'.format(corpus_graph_terms),
        'query': """
select ?termUri ?name ?score where {{
  ?termUri <http://schema.semantic-web.at/ppcm/2013/5/combinedRelevanceScore> ?score .
  ?termUri <http://schema.semantic-web.at/ppcm/2013/5/name> ?name .
  filter (?score > {})
}} order by desc(?score)""".format(crs_threshold),
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


def query_sparql_endpoint(sparql_endpoint, query=all_data_q):
    graph = rdflib.ConjunctiveGraph('SPARQLStore')
    rt = graph.open(sparql_endpoint)
    rs = graph.query(query)
    return rs


def get_ridfs(sparql_endpoint, termsgraph):
    q_term_scores = """
    select distinct ?lemma ?ridf ?crs where {{
      GRAPH <{}> {{
        ?s <http://schema.semantic-web.at/ppcm/2013/5/textValue> ?lemma .
        ?s <http://schema.semantic-web.at/ppcm/2013/5/ridfTermScore> ?ridf .
        ?s <http://schema.semantic-web.at/ppcm/2013/5/combinedRelevanceScore> ?crs .
      }}  
    }}
    """.format(termsgraph)
    rs = query_sparql_endpoint(sparql_endpoint, q_term_scores)
    results = dict()
    for r in rs:
        results[str(r[0])] = float(r[2])
    return results


def query_cpt_cooc_scores(sparql_endpoint, cpt_cooc_graph):
    q_cooc_score = """
select distinct ?cpt1 ?cpt2 ?score where {{
  GRAPH <{}> {{
  ?cpt1 <http://schema.semantic-web.at/ppcm/2013/5/hasConceptCooccurrence> ?o .
  ?o <http://schema.semantic-web.at/ppcm/2013/5/cooccurringExtractedConcept> ?cpt2 .
  ?o <http://schema.semantic-web.at/ppcm/2013/5/score> ?score
  }}
}}
""".format(cpt_cooc_graph)
    rs = query_sparql_endpoint(sparql_endpoint, q_cooc_score)
    dist_mx = dict()
    for r in rs:
        cpt1 = str(r[0])
        cpt2 = str(r[1])
        score = float(r[2])
        try:
            dist_mx[cpt1][cpt2] = score
        except KeyError:
            dist_mx[cpt1] = {cpt2: score}
        try:
            dist_mx[cpt2][cpt1] = score
        except KeyError:
            dist_mx[cpt2] = {cpt1: score}
    return dist_mx


def query_terms2cpts_cooc_scores(sparql_endpoint, cpt_cooc_graph, terms_graph):
    q_cooc_cpt_score = """
    select distinct ?tv (group_concat(?cpt;separator="|") as ?cpts) (group_concat(?c_score;separator="|") as ?c_scores) where {{
      ?s <http://schema.semantic-web.at/ppcm/2013/5/hasConceptCooccurrence> ?co_cpt .
      ?s <http://schema.semantic-web.at/ppcm/2013/5/textValue> ?tv .
      ?co_cpt <http://schema.semantic-web.at/ppcm/2013/5/cooccurringExtractedConcept> ?cpt .
      ?co_cpt <http://schema.semantic-web.at/ppcm/2013/5/score> ?c_score .
    }}
    """
    q_cooc_term_score = """
    select distinct ?tv (group_concat(?cooc_term;separator="|") as ?cooc_terms) (group_concat(?t_score;separator="|") as ?t_scores) where {{
      ?s <http://schema.semantic-web.at/ppcm/2013/5/textValue> ?tv .
      ?s <http://schema.semantic-web.at/ppcm/2013/5/hasTermCooccurrence> ?co_term .
      ?co_term <http://schema.semantic-web.at/ppcm/2013/5/cooccurringExtractedTerm> ?term_view .
      ?term_view <http://schema.semantic-web.at/ppcm/2013/5/textValue> ?cooc_term .
      ?co_term <http://schema.semantic-web.at/ppcm/2013/5/score> ?t_score .
    }}
    """

    q_cooc_cpt_score = """
select distinct ?tv (group_concat(?cpt;separator="|") as ?cpts) (group_concat(?c_score;separator="|") as ?c_scores) where {{
  GRAPH <{cooc_graph}> {{
    ?s <http://schema.semantic-web.at/ppcm/2013/5/hasConceptCooccurrence> ?co_cpt .
    ?co_cpt <http://schema.semantic-web.at/ppcm/2013/5/cooccurringExtractedConcept> ?cpt .
    ?co_cpt <http://schema.semantic-web.at/ppcm/2013/5/score> ?c_score .
  }} .
  GRAPH <{terms_graph}>
  {{
    ?s <http://schema.semantic-web.at/ppcm/2013/5/textValue> ?tv .
  }}
}}
""".format(cooc_graph=cpt_cooc_graph, terms_graph=terms_graph)
    cpt_rs = query_sparql_endpoint(
        sparql_endpoint, query=q_cooc_cpt_score
    )
    cooc_dict = dict()
    for r in cpt_rs:
        text_value, cooc_cpts, t_scores = r
        cooc_cpts = cooc_cpts.split('|')
        t_scores = list(map(float, t_scores.split('|')))
        cpts_scores = dict(zip(cooc_cpts, t_scores))
        cooc_dict[text_value.toPython()] = cpts_scores
    return cooc_dict


if __name__ == '__main__':
    pass
