# Function sets the value of TXA 2 to "CON" and
# sets the value of TXA 13 to the original value
# in TXA 2

def update_txa_2_13(json_in):

    for (s, value) in json_in.items():
        if s.startswith('TXA') and len(json_in[s]['2']) > 0:
            txa_val = json_in[s]['2']
            json_in[s].update({'13': txa_val})
            json_in[s].update({'2': 'CON'})
            break

    return json_in
