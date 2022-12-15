# Function updates PV1 16 and PV1 18 for the XTEND
# application, to set VIP Indicator and Patient Type

from oasis_fun import get_codetable


def update_pv1_16_18(json_in, key, env):
    
    pv1_18 = ""
    pv1 = dict()
    
    xtend_dict = get_codetable.get_codetable(key, env)
    for (k, value) in json_in.items():
        if k.startswith('PV1'):
            pv1 = json_in[k]
            pv1_18 = pv1['18']
            break

    for d in xtend_dict:
        if d['input'] == pv1_18:
            pv1_16 = d['output']
            pv1.update({'16': pv1_16})
            new_pv1_18 = (":"+pv1_18)
            pv1.update({'18': new_pv1_18})
        else:
            pv1.update({'18': ":"})
            break

    return json_in
