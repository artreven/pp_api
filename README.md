# pp_api
This package provides classes `PoolParty` and `GraphSearch` to wrap around [PoolParty APIs](https://help.poolparty.biz/doc/developer-guide/enterprise-server-apis/entity-extractor-apis) and [GraphSearch APIs](https://help.poolparty.biz/doc/developer-guide/semantic-integrator-apis/graphsearch-api).

## `PoolParty` class (in `pp_api.pp_calls`)
Provides a wrapper around PoolParty APIs. The class initializator expects a `server` URL string to know where to find the PoolParty - the only required parameter.
The credentials can be either explicitly supplied or read from the environmental variables. The methods of the class map to the respective API methods of PP.

## `GraphSearch` class (in `pp_api.gs_calls`)
Provides a wrapper around GraphSearch APIs. Also expects a `server` and optionally credentials.

_____
For an example of using this package see [`pp_vectorizer`](https://github.com/semantic-web-company/pp_vectorizer).
