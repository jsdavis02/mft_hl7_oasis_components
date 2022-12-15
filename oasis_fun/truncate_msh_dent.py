# Function updates the MSH segment, truncating it to 16 fields

import itertools

def truncate_msh_dent(json_in):

    for (s, value) in json_in.items():
        if s.startswith('MSH'):
            new_dict = dict(itertools.islice(json_in[s].items(), 16))
            json_in[s] = new_dict
            break

    return json_in

