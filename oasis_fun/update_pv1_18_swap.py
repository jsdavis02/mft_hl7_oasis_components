# Function sets patient type to ":" for both patients
# in a Patient Swap event, A17

def update_pv1_18_swap(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PV1'):
            json_in[s].update({'18': ":"})

    return json_in
