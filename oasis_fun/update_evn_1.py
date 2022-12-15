# Function updates the EVN segment when a ADT-A08
# becomes a discharge, ADT-A03

def update_evn_1(json_in):

    evn = dict()
    msh = dict()
    pv1_45_val = ""

    for (s, value) in json_in.items():
        if s.startswith('PV1'):
            pv1 = json_in[s]
            pv1_45_val = pv1['45']
            break

    for (s, value) in json_in.items():
        if s.startswith('EVN'):
            evn = json_in[s]
            break

    for (s, value) in json_in.items():
        if s.startswith('MSH'):
            msh = json_in[s]
            break

    if len(pv1_45_val) > 0:
        evn.update({'1': "A03"})
        msh.update({'9': "ADT^A03"})

    return json_in
