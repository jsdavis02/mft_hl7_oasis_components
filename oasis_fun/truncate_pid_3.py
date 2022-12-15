# Function updates PID 3, truncating by removing the leading
# zeroes in the patient id.

def truncate_pid_3(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PID'):
            pid_3 = json_in[s]['3'].split("^")
            string = pid_3[0].lstrip("0")
            json_in[s].update({'3': string+"^^^SMRN^SMRN"})

    return json_in
