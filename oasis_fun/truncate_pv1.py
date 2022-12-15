# Function updates the PV! segment, truncating it to 46 fields

import itertools

def truncate_pv1(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PV1'):
            new_dict = dict(itertools.islice(json_in[s].items(), 46))
            json_in[s] = new_dict
            break

    return json_in
