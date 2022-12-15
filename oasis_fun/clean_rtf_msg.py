# Function removes pdf segments from Endosoft message for
# further processing.

def clean_rtf_msg(rtf_json):

    deletekeys = list()
    for (s, value) in rtf_json.items():
        if s.startswith('OBX') and rtf_json[s]['2'] == "ED":
            deletekeys.append(s)

    for s in deletekeys:
        if s in rtf_json:
            del rtf_json[s]
  
    return rtf_json
