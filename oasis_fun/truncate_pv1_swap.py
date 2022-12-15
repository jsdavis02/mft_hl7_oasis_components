# Function updates the PV1 segment, truncating it to
# 50 fields for a patient swap.

import itertools

def truncate_pv1_swap(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PV1'):
            new_dict = dict(itertools.islice(json_in[s].items(), 50))
            json_in[s] = new_dict

    return json_in
