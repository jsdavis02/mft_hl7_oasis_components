# Function updates the MSH segment to update the sending
# application

def update_msh_3_dent(json_in):

    for (s, value) in json_in.items():
        if s.startswith('MSH'):
            json_in[s].update({'3': "DENTRIX"})
            break

    return json_in
