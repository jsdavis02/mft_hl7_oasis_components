# Function updates the MSH segment, field 11,
# processing ID to P from D.

def update_msh_11(json_in):

    for (s, value) in json_in.items():
        if s.startswith('MSH') and json_in[s]['11'] == "D":
            json_in[s].update({'11': "P"})

    return json_in
