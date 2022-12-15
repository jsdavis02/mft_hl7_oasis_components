# Function updates the PV2 segment, truncating it to
# 32 fields for a patient swap.

import itertools

def truncate_pv2_swap(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PV2'):
            new_dict = dict(itertools.islice(json_in[s].items(), 32))
            json_in[s] = new_dict

    return json_in
