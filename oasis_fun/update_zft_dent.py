# Function updates ZFT segment with dental procedure details,
# if the data is there, otherwise it will create an empty segment
# of 26 fields.

def update_zft_dent(json_in):

    for (s, value) in json_in.items():
        if s.startswith('ZFT'):
            json_in[s].update({'3': ""})
            i = len(json_in[s])
            while i < 27 and i not in json_in[s].items():
                json_in[s].update({i: ""})
                i += 1
            break

    for (s, value) in json_in.items():
        if s.startswith('ZFT') and len(str(json_in[s]['1'])) > 0:
            zft_1 = json_in[s]['1']
            json_in[s].update({'20': zft_1})
            json_in[s].update({'1': ""})
            break

        if s.startswith('ZFT') and len(str(json_in[s]['2'])) > 0:
            zft_2 = json_in[s]['2']
            zft_2s = (zft_2+"~")
            json_in[s].update({'21': zft_2s})
            json_in[s].update({'2': ""})
            break

    return json_in

