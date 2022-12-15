# Function updates the PID segment, patient address
# where country and country code are deleted

def update_pid_11(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PID'):
            pid_id = json_in[s]['11']
            string = pid_id.split("^")[:5]
            new_string = "^".join(string)
            json_in[s].update({'11': new_string})

    return json_in

