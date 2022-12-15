# Function creates a new NTE, notes segment and moves the
# information in TXA 13 to field three of the NTE segment

def update_nte_3(json_in):

    for (s, value) in json_in.items():
        if s.startswith('TXA')and len(json_in[s]['13']) > 0:
            nte = {'1': "", '2': "", '3': json_in[s]['13'], '4': ""}
            json_in.update({'NTE.'+str(len(json_in)): nte})
            break

    return json_in
