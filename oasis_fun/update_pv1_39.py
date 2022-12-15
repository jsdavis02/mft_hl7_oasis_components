# Function performs a db lookup to determine the
# value of PV1 39, servicing facility, by looking up the code based on 
# PV1 3

from . import get_codetable


def update_pv1_39(json_in, key, env):

    pv1 = dict()
    def_val = ""
  
    for (s, value) in json_in.items():
        if s.startswith('PV1'):
            pv1 = json_in[s]
            break
    tbl_dict = get_codetable.get_codetable(key, env)
    found = False
    for d in tbl_dict:
        if d['input'] == pv1['3'].split("^")[0]:
            pv1.update({'39': d['output']})
            found = True
        elif d['input'] == "no_match":
            def_val = d['output']
    if not found:
        pv1.update({'39': def_val})
    
    return json_in
