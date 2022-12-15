# Function updates PV2, expected admit date, truncating
# the timestamps, when the message is a Patient Swap, A17.

def truncate_pv2_8(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PV2'):
            string = json_in[s]['8']
            short_str = string[0:8]
            json_in[s].update({'8': short_str})

    return json_in
