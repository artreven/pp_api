import os
import pp_api.pp_calls as pp
import NIF21
import uuid
from decouple import config


class NIFAnnotator():
    """
        Objects of this class are associated with a thesaurus in a PoolParty
        instance. The instance details and the thesaurus ID are given as
        parameters to the init.
    """
    def __init__(self,
                 pp_url=config("server"),
                 pp_usr=config("pp_user"),
                 pp_pwd=config("pp_password"),
                 pp_pid=config("pp_pid")):
        self.pp = pp.PoolParty(server=pp_url,
                               auth_data=(pp_usr, pp_pwd))
        self.pp_pid = pp_pid


    def create_annotated_nif(self,
                            text,
                            doc_uri="http://example.doc/"+str(uuid.uuid4())):
        """
        Annotates a document with entities found in this objects thesaurus. 
        The original document and the annotations are returned as NIF.
        :param text: 
        :param doc_uri: 
        :return: 
        """
        nif21 = NIF21.NIF21()
        nif21.context(doc_uri,
                      0,
                      len(text),
                      text)

        cpts = self._extract(text)
        positions = self._get_positions(cpts)
        for uri, start, end, label in positions:
            nif21.bean(label,
                       start,
                       end,
                       None,
                       1,
                       None,
                       uri,
                       None)

        return nif21.turtle()

    def _extract(self,
                 text):
        extra_extract_args = {"showMatchingPosition": True,
                              "numberOfTerms": 0}
        r = self.pp.extract(text, pid=self.pp_pid, **extra_extract_args)
        cpts = self.pp.get_cpts_from_response(r)
        return cpts

    def _get_positions(self, cpts):
        result = []
        for c in cpts:
            uri = c['uri']
            label = c['prefLabel']
            for ma in c['matchings']:
                for pos in ma['positions']:
                    result.append((uri, pos[0], pos[1], label))
        return result