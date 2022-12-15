# Function updates PID 5, truncating to include
# given name, middle name or initial and surname.

def truncate_pid_5(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PID'):
            string = json_in[s]['5'].split("^")
            json_in[s].update({'5': string[0]+"^"+string[1]+"^"+string[2]})

    return json_in
