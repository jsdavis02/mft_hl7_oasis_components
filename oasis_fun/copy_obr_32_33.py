def copy_obr_32_33(json_in):
    for (s, value) in json_in.items():
        if s.startswith('OBR'):
            if len(json_in[s]['33']) <= 0:
                json_in[s].update({'33': json_in[s]['32']})
    return json_in