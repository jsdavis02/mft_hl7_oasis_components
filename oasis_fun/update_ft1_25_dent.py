# Function updates the FT1 25 segment
# to update Procedure code.

def update_ft1_25_dent(json_in):

    for (s, value) in json_in.items():
        if s.startswith('FT1'):
            ft1_25 = json_in[s]['25']
            new_val = (ft1_25+"^^BEAP")
            json_in[s].update({'25': new_val})
            break

    return json_in

