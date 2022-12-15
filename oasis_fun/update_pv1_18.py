# Function updates PV1 18 through a db lookup of the visit site id
# from PV1 3, and sets PV1 18

from . import get_codetable


def update_pv1_18(json_in, key, env):
    
    def_val = ""
    pv1 = dict()

    for (s, value) in json_in.items():
        if s.startswith('PV1'):
            pv1 = json_in[s]
            break
    tbl_dict = get_codetable.get_codetable(key, env)
    found = False
    for d in tbl_dict:
        if d['input'] == pv1['3'].split("^")[0]:
            pv1.update({'18': d['output']})
            found = True
        elif d['input'] == "no_match":
            def_val = d['output']
    if not found:
        pv1.update({'18': def_val})

    return json_in
