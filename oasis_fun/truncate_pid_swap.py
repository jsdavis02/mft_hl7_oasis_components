# Function updates the PID segment, truncating it to
# 30 fields for a patient swap.

import itertools

def truncate_pid_swap(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PID'):
            new_dict = dict(itertools.islice(json_in[s].items(), 30))
            json_in[s] = new_dict

    return json_in
