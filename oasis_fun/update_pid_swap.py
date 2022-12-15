# Function updates PID 2 and 3 segments where there are
# multiple PID values (ADT-A17, patient swap)


def update_pid_swap(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PID'):
            new_string = json_in[s]['3'].split("^")
            is_epi = (new_string[3])

            if is_epi == 'EPI':
                new_pid_2 = (new_string[0]+"^^^"+new_string[3]+"^PE")
                json_in[s].update({'2': new_pid_2})
                newer_string = (new_string[4].split("~"))
                new_pid_3 = (newer_string[1]+"^^^SMRN^SMRN")
                json_in[s].update({'3': new_pid_3})

    return json_in
