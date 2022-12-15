# Function updates the OBR segment, filler order number
# for Endovault, if message is RTF or PDF.

def update_obr_3_endo(rtf_json, pdf_json):

    jsons = (rtf_json, pdf_json)

    for j in jsons:
        for (s, value) in j.items():
            if s.startswith('OBR'):
                j[s].update({'2': ""})
                obr_3 = j[s]['3']
                obr_4 = j[s]['4']
                string = obr_4.split("^")
                j[s].update({'3': obr_3+string[0]})

    return rtf_json, pdf_json

