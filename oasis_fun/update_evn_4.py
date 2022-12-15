# Function updates the EVN segment, event reason code
# for a patient swap event, ADT-A17

def update_evn_4(json_in):

    for (s, value) in json_in.items():
        if s.startswith('EVN') and json_in[s]['4'] == "ADT_EVENT":
            json_in[s].update({'4': "ADT"})

    return json_in
