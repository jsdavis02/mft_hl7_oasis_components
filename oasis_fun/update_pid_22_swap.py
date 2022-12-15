# Function updates PID 22, Ethnic Group truncating
# to three chars, when the message is a Patient Swap, A17.

def update_pid_22_swap(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PID'):
            string = json_in[s]['22']
            short_str = string[0:3]
            json_in[s].update({'22': short_str})

    return json_in
