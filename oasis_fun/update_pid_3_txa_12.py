# Function performs multiple updates to the PID and TXA
# segments

def update_pid_3_txa_12(json_in):
   
    pid = dict()
    txa = dict()
   
    for (s, value) in json_in.items():
        if s.startswith('PID'):
            pid = json_in[s]
            break
            
    for (s, value) in json_in.items():
        if s.startswith('TXA'):
            txa = json_in[s]
            break
            
    pid_3_val = pid['3']
    new_stringp = pid_3_val.split("^")
    patient_id = (new_stringp[0])

    if len(patient_id) > 0:
        pad_patient_id = (new_stringp[0].zfill(10))
        new_patient_id = (pad_patient_id+"^^SMRN^SMRN")
        pid.update({'3': new_patient_id})

    txa_12_val = txa['12']
    new_stringt = txa_12_val.split("^")
    doc_id = (new_stringt[2])
    
    # Pad document id with a leading "C" and two empty fields
    if len(doc_id) > 0:
        new_doc_id = ("^^C"+new_stringt[2])
        txa.update({'12': new_doc_id})

    return json_in
