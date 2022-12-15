# Function deletes PID segment, field 18

def delete_pid_23(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PID'):
            json_in[s].update({'23': ""})
            break

    return json_in
