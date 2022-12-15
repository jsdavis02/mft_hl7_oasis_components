# Function updates the ORC segment, truncating it to 13 fields
import itertools


def truncate_orc(json_in, fcount):

    for (s, value) in json_in.items():
        if s.startswith('ORC'):
            new_dict = dict(itertools.islice(json_in[s].items(), fcount))
            json_in[s] = new_dict
            break

    return json_in
