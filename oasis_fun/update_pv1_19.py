# Function updates PV1 19 with the value of PID 18,
# and clears PV1 3

def update_pv1_19(json_in):
    
    pv1_19_val = ""
    
    for (s, value) in json_in.items():
        if s.startswith('PID') and len(str(json_in[s]['18'])) > 0:
            pv1_19_val = json_in[s]['18']
            break

    for (s, value) in json_in.items():
        if s.startswith('PV1'):
            pv1 = json_in[s]
            pv1.update({'3': ""})
            pv1.update({'19': pv1_19_val})
            break

    return json_in
