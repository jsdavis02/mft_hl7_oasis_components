# Function removes pdf segments from Endosoft message for
# further processing.

def split_endo_msgs(pdf_json, rtf_json):

    deletekeys = list()
    for (s, value) in pdf_json.items():
        if s.startswith('OBX') and pdf_json[s]['2'] == "TX":
            deletekeys.append(s)

    for s in deletekeys:
        if s in pdf_json:
            del pdf_json[s]

    deletekeys = list()
    for (s, value) in rtf_json.items():
        if s.startswith('OBX') and rtf_json[s]['2'] == "ED":
            deletekeys.append(s)

    for s in deletekeys:
        if s in rtf_json:
            del rtf_json[s]

    return pdf_json, rtf_json
