# Function deletes PID segment, field 18

def delete_pid_18(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PID'):
            json_in[s].update({'18': ""})
            break

    return json_in
