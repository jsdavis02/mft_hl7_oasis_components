# Function updates the PID 3 segments
# to update Facility information.

def update_pid_3_dent(json_in):

    pid_id = ""
    s = ""
    for (s, value) in json_in.items():
        if s.startswith('PID'):
            pid_id = json_in[s]['3']
            break

    if len(pid_id) > 0:
        new_pid_3 = (pid_id+"^^^SMRN^SMRN")
        json_in[s].update({'3': new_pid_3})

    return json_in

