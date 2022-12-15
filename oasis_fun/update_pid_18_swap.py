# Function updates PID 18, patient account number
# with visit number from PV1 19 for a patient swap.

def update_pid_18_swap(json_in):

    pv1_keys = list()
    pid_keys = list()

    for (s, value) in json_in.items():
        if s.startswith('PV1'):
            pv1_keys.append(s)

    for (s, value) in json_in.items():
        if s.startswith('PID'):
            pid_keys.append(s)

    new_dict = dict(zip(pv1_keys, pid_keys))

    for (s, value) in new_dict.items():
        pv1_val = json_in[s]['19']
        json_in[value].update({'18': pv1_val})

    return json_in
