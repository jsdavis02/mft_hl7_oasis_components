# Function updates the FT1 segment,
# fields 2, 11, 16, and 20.

def update_ft1_dent(json_in):

    for (s, value) in json_in.items():
        if s.startswith('FT1'):
            json_in[s].update({'2': ""})
            json_in[s].update({'11': ""})
            json_in[s].update({'16': ""})
            json_in[s].update({'20': ""})
            break

    return json_in
