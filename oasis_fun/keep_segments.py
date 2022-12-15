# Function deletes unnecessary segments based on
# a list object is passed from the route wrapper script.


def keep_segments(json_in, seglist):
    # print(list(json_in))
    for key in list(json_in):
        if not key.startswith(seglist):
            del json_in[key]

    return json_in
