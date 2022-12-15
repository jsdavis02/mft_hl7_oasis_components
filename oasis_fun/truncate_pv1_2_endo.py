# Function updates PV1, truncating patient class
# to one char.

def truncate_pv1_2_endo(rtf_json, pdf_json):

    jsons = (rtf_json, pdf_json)
    for j in jsons:
        for (s, value) in j.items():
            if s.startswith('PV1'):
                string = j[s]['2']
                short_str = string[0:1]
                j[s].update({'2': short_str})

    return rtf_json, pdf_json
