# Function deletes PV1 field 3, Patient Location

def delete_pv1_3_dent(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PV1'):
            json_in[s].update({'3': ""})
            break

    return json_in
