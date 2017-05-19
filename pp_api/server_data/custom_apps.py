server = 'https://custom_apps.poolparty.biz'
pid = '1DF14F0D-DE59-0001-B2F4-8FBA1C3015CA'
corpus_id = 'corpus:84c87cdf-e2a4-4882-ace1-535f91426283'
corpusgraph_id = 'corpusgraph:' + corpus_id[7:]
termsgraph_id = corpusgraph_id + ':extractedTerms'
cpt_occur_graph_id = corpusgraph_id + ':conceptOccurrences'
cpt_cooc_graph = corpusgraph_id + ':cooccurrence'
sparql_endpoint = 'http://custom-virtuoso.semantic-web.at:8890/sparql'