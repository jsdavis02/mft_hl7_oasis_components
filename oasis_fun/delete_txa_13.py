# Function deletes TXA segment, field 13

def delete_txa_13(json_in):

    for (s, value) in json_in.items():
        if s.startswith('TXA'):
            json_in[s].update({'13': ""})
            break

    return json_in
