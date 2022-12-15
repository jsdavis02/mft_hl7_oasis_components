# Function performs a db lookup to set the value
# of TXA 19 to the code value based on the value
# of PV1 19

from oasis_fun import get_codetable


def update_txa_19(json_in, key, env):

    txa = dict()
    pv1_19 = ""
    
    xtend_dict = get_codetable.get_codetable(key, env)
    # Find value of TXA-19
    # Determine document type from TXA-19
    for (s, value) in json_in.items():
        if s.startswith('TXA'):
            txa = json_in[s]
            pv1_19 = txa['19']
            break

    for d in xtend_dict:
        if d['input'] == pv1_19:
            new_pv1_19 = d['output']
            txa.update({'19': new_pv1_19})
            break

    return json_in
