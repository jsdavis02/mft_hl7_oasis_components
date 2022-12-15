# Function updates the PV1 segment, truncating it to
# 6 fields for a patient swap.

import itertools

def truncate_evn_swap(json_in):

    for (s, value) in json_in.items():
        if s.startswith('EVN'):
            new_dict = dict(itertools.islice(json_in[s].items(), 6))
            json_in[s] = new_dict

    return json_in
