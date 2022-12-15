# Function updates the MSH segment with the version id
# Version id is passed from the route wrapper script.

def update_msh_12(json_in, version):

    for (s, value) in json_in.items():
        if s.startswith('MSH'):
            json_in[s].update({'12': version})
            break

    return json_in
