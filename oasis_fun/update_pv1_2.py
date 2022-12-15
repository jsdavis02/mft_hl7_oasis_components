# Function sets the patient class to O if PV1-2 (patient class) is not I or O

def update_pv1_2(json_in):
    for (s, value) in json_in.items():
        if s.startswith('PV1') and len(json_in[s]['2']) > 0:
            patclass_val = json_in[s]['2']
            if patclass_val != 'I' or 'O':
                json_in[s].update({'2': 'O'})
        break
    return json_in
