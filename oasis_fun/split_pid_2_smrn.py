# Function updates PID 2 and 3 segments where there are
# multiple PID values (ADT-A17, patient swap)

def split_pid_2_smrn(json_in):

    pid_id = ""
    for (s, value) in json_in.items():
        if s.startswith('PID'):
            pid_id = json_in[s]['3']
            break

    new_string = pid_id.split("^")
    is_epi = (new_string[3])
    if is_epi == 'EPI':
        new_pid_2 = (new_string[0]+"^^^"+new_string[3]+"^PE")
        json_in[s].update({'2': new_pid_2})
        newer_string = (new_string[4].split("~"))
        new_pid_3 = (newer_string[1]+"^^^SMRN^SMRN")
        json_in[s].update({'3': new_pid_3})

    return json_in
