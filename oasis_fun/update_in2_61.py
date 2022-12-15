# Function updates the IN2 segments with the ZIN field

def update_in2_61(json_in):

    zin_val = ""

    for (s, value) in json_in.items():
        if s.startswith('ZIN') and len(json_in[s]['19']) > 0:
            zin_val = json_in[s]['19']
            break

    for (s, value) in json_in.items():
        if s.startswith('IN2') and len(zin_val) > 0:
            json_in[s].update({'61': zin_val})

    return json_in

