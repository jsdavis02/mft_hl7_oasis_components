# Function updates the MSH segment, truncating it to 12 fields

import itertools

def truncate_msh(json_in):

    for (s, value) in json_in.items():
        if s.startswith('MSH'):
            new_dict = dict(itertools.islice(json_in[s].items(), 12))
            json_in[s] = new_dict
            break

    return json_in
