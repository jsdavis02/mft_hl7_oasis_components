# Function evaluates for the message kill criteria,
# based on department.

from oasis_fun import get_criteria


def dept_kill_criteria(json_in, route_id, env):

    pv1 = dict()

    for (s, value) in json_in.items():
        if s.startswith('PV1'):
            pv1 = json_in[s]
            break
    tbl_dict = get_criteria.get_criteria(route_id, env)

    result = "true"
    for d in tbl_dict:
        if d['operator'] == 'eq' and d['value'] == pv1['3'].split("^")[0]:
            result = "false"
            break

    return result
