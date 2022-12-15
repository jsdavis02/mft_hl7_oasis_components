# Function updates the ORC segment, truncating it to 13 fields

import itertools

def truncate_segment(json_in, segment, field_count):

    for (s, value) in json_in.items():
        if s.startswith(segment):
            new_dict = dict(itertools.islice(json_in[s].items(), field_count))
            json_in[s] = new_dict
            break

    return json_in
