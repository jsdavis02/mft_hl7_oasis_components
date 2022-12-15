# Function updates the PID segment for the Endovault messages

def update_pid_endo(rtf_json, pdf_json):

    jsons = (rtf_json, pdf_json)

    for j in jsons:
        for (s, value) in j.items():
            if s.startswith('PID'):
                pid_id = j[s]['2'].split("^")
                new_pid_3 = (pid_id[0]+"^^^SMRN^SM")
                j[s].update({'2': new_pid_3})

    return rtf_json, pdf_json

