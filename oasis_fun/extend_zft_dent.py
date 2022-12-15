# Function updates the ZFT segment, creating 26 empty fields


def extend_zft_dent(json_in):

    for (s, value) in json_in.items():
        if s.startswith('ZFT'):
            json_in[s] = {}
            i = 1
            while i < 27:
                json_in[s].update({i: ""})
                i += 1

    return json_in


