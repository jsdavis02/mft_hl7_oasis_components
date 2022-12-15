# Function updates PV2, visit type truncating
# to two chars, when the message is a Patient Swap, A17.

def truncate_pv2_7_swap(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PV2'):
            string = json_in[s]['7']
            short_str = string[0:2]
            json_in[s].update({'7': short_str})

    return json_in
