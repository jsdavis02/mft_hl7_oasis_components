from operator import itemgetter

def trim_trailing_empty_fields(json_in):
    # we build a segment-field notation list
    removelist = []
    for (s, value) in json_in.items():
        # maybe try getting keys then looping the keys in reverse.
        rkeys = sorted(json_in[s].keys(), key=int, reverse=True)
        for k in rkeys:
            if len(json_in[s][k]) <= 0:
                removelist.append(s+'-'+k)
            else:
                break
    # now loop through remove list and del
    # doing this instead of deleting in above loop
    # because we are looping through json_in, can't delete items in object
    # while that is the object your looping over
    for r in removelist:
        # print(r)
        segment, field = r.split('-')
        # print(json_in[segment][field])
        del json_in[segment][field]
    return json_in
