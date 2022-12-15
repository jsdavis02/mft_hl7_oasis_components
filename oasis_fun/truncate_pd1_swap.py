# Function updates the PD1 segment, truncating it to
# 3 fields for a patient swap.

import itertools

def truncate_pd1_swap(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PD1'):
            new_dict = dict(itertools.islice(json_in[s].items(), 3))
            json_in[s] = new_dict

    return json_in
