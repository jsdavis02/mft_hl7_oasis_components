# Function updates the TXA segment, document type
# for Endovault, if message is RTF or PDF.

def update_txa_2_endo(rtf_json, pdf_json):

    txa_seg = ()
    jsons = (rtf_json, pdf_json)

    for j in jsons:
        for (s, value) in j.items():
            if s.startswith('TXA'):
                txa_seg = j[s]
                break

        for (s, value) in j.items():
            if s.startswith('OBX') and j[s]['2'] == "ED":
                txa_seg.update({'2': "ENDOPDF"})
            else:
                txa_seg.update({'2': "ORDENDO"})

    return rtf_json, pdf_json

