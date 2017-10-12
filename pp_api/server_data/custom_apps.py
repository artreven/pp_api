server = 'https://custom_apps.poolparty.biz'
sparql_endpoint = 'http://custom-virtuoso.semantic-web.at:8890/sparql'
pp_sparql_endpoint = server + '/PoolParty/sparql/'

# cocktails
pid = '1DF14F0D-DE59-0001-B2F4-8FBA1C3015CA'
p_name = 'cocktails'
corpus_id = 'corpus:84c87cdf-e2a4-4882-ace1-535f91426283'
corpusgraph_id = 'corpusgraph:' + corpus_id[7:]
termsgraph_id = corpusgraph_id + ':extractedTerms'
cpt_occur_graph_id = corpusgraph_id + ':conceptOccurrences'
cpt_cooc_graph = corpusgraph_id + ':cooccurrence'

# CHEBI
chebi_pid = '1DF15F72-6082-0001-B1E7-1520A950D6C0'
chebi_corpus_id = 'corpus:704c1cfa-87bf-48c3-bf2d-145aea748bd9'

# Reegle
reegle_pid = '1DF18085-04D9-0001-60F8-1E4F1194EA30'

#Enriched EuroVoc
ee_pid = '1DF187B6-1C2A-0001-D481-1FA01F909830'
