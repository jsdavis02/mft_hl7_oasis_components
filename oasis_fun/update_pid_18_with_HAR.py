# Function copies the HAR in PV1-50 to PID-18
# segments

def update_pid_18_with_HAR(json_in):
    pid = dict()

    for (s, value) in json_in.items():
        if s.startswith('PID'):
            pid = json_in[s]
            break

    for (s, value) in json_in.items():
        if s.startswith('PV1') and len(json_in[s]['50']) > 0:
            pv1_50_val = json_in[s]['50']
            pid.update({'18': pv1_50_val})
            break
    return json_in
