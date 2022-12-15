# Function evaluates for the message kill criteria,
# based on procedure code in Dentrix.

from oasis_fun import get_criteria


def code_kill_criteria(json_in, route_id, env):

    ft1 = dict()

    for (s, value) in json_in.items():
        if s.startswith('FT1'):
            ft1 = json_in[s]
            break
    tbl_dict = get_criteria.get_criteria(route_id, env)
    result = "true"
    for d in tbl_dict:
        if d['operator'] == 'eq' and d['value'] == ft1['7']:
            result = "false"
            break

    return result
