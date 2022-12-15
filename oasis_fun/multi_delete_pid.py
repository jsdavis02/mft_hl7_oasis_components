# Function deletes multiple fields in PID segment

def multi_delete_pid(json_in):

    for (s, value) in json_in.items():
        if s.startswith('PID'):
            field_list = ["10", "11", "13", "14", "15", "16", "17", "19", "20", "21", "22", "23", "24", "25", "26", "27", "29", "31", "32"]
            for field in field_list:
                json_in[s].update({field: ""})
            break

    return json_in
