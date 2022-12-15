# Function deletes unnecessary segments based on
# a list object is passed from the route wrapper script.

def delete_segments(json_in, seglist):

    deletekeys = list()
    for (key, value) in json_in.items():
        if key.startswith(seglist):
            deletekeys.append(key)

    for key in deletekeys:
        if key in json_in:
            del json_in[key]

    return json_in
