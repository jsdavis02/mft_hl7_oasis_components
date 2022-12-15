# Function updates PID 12, County Code truncating
# to four chars, when the message is a Patient Swap, A17.

def update_pid_12_swap(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PID'):
            string = json_in[s]['12']
            short_str = string[0:4]
            json_in[s].update({'12': short_str})

    return json_in
