# Function updates PV1, patient type truncating
# to two chars, when the message in a Patient Swap, A17.

def truncate_pv1_18(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PV1'):
            string = json_in[s]['18']
            short_str = string[0:2]
            json_in[s].update({'18': short_str})

    return json_in
