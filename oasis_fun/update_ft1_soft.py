# Function updates FT1 segment with transaction details, and extends
# the segment to 25 fields.

def update_ft1_soft(json_in):

    for (s, value) in json_in.items():
        if s.startswith('FT1'):
            json_in[s].update({'2': ""})
            json_in[s].update({'8': ""})
            i = len(json_in[s])+1
            while i < 26 and i not in json_in.items():
                json_in[s].update({i: ""})
                i += 1
            break

    string = (json_in[s]['7']+"^^BEAP")
    json_in[s].update({'25': string})

    return json_in

