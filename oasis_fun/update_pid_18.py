# Function updates PID 18, patient account number
# with visit number from PV1 19.


def update_pid_18(json_in):

    pid18_val = ""

    for (s, value) in json_in.items():
        if s.startswith('PV1'):
            pid18_val = json_in[s]['19']
            break

    for (s, value) in json_in.items():
        if s.startswith('PID') and len(json_in[s]['18']) <= 0:
            json_in[s].update({'18': pid18_val})
            break

    return json_in

