# Function updates the PID sections for two patients,
# truncating the repeated field in PID 9, patient name.
# If PID 9 includes a middle name or initial, it is
# included, if not, the element is truncated further.

def truncate_pid_9_swap(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PID') and len(json_in[s]['9']) > 0:
            val_9 = json_in[s]['9'].split("^")
            if len(val_9[2]) == 0:
                    new_val_9 = val_9[0]+"^"+val_9[1]
                    json_in[s].update({'9': new_val_9})
            elif len(val_9[2]) > 0:
                new_val_9 = val_9[0]+"^"+val_9[1]+"^"+val_9[2]
                json_in[s].update({'9': new_val_9})

    return json_in
