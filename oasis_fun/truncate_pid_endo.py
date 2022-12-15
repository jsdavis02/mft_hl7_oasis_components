# Function updates the PID segment, truncating it to 13 fields

import itertools

def truncate_pid_endo(rtf_json, pdf_json):

    jsons = (rtf_json, pdf_json)

    for j in jsons:
        for (s, value) in j.items():
            if s.startswith('PID'):
                new_dict = dict(itertools.islice(j[s].items(), 13))
                j[s] = new_dict
                break

    return rtf_json, pdf_json
