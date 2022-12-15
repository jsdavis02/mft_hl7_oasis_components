# Function performs a db lookup to determine the
# value of PV1 39, servicing facility, by looking up the code based on 
# PV1 3

from oasis_fun import get_codetable


def update_pv1_2_with_table(json_in, key, env):


    pv2_7_val = []
    i = 0
    for (s, value) in json_in.items():
        if s.startswith('PV2'):
            pv2_7_val.append(json_in[s]['7'])
    if len(pv2_7_val) > 0:
        tbl_dict = get_codetable.get_codetable(key, env)
        for (s, value) in json_in.items():
            if s.startswith('PV1'):
                if len(pv2_7_val) >= i+1:
                    for d in tbl_dict:
                        if d['input'] == pv2_7_val[i]:
                            json_in[s].update({'2': d['output']})
                            break
                i += 1

    return json_in
