# Function removes pdf segments from Endosoft message for
# further processing.

def clean_pdf_msg(pdf_json):

    deletekeys = list()
    for (s, value) in pdf_json.items():
        if s.startswith('OBX') and pdf_json[s]['2'] == "TX":
            deletekeys.append(s)

    for s in deletekeys:
        if s in pdf_json:
            del pdf_json[s]

    return pdf_json
