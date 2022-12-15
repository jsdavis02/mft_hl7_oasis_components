# Function updates PV1 10, Hospital Service truncating
# to three chars, when the message is a Patient Swap, A17.

def update_pv1_10_swap(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PV1'):
            string = json_in[s]['10']
            short_str = string[0:3]
            json_in[s].update({'10': short_str})

    return json_in
