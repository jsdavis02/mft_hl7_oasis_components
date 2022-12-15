# Function updates the PV1 sections for two patients,
# truncating the repeated field in PID 13, patient
# contact information.

def truncate_pv1_13_swap(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PID'):
            val_13 = json_in[s]['13'].split("~")
            new_val_13 = val_13[0]
            json_in[s].update({'13': new_val_13})

    return json_in
