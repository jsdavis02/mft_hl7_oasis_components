# Function checks for any criteria on a route and returns
# true if there is none, and the message should be routed,
# or false if there is criteria, and the message should not
# be routed.
from oasis_fun import get_criteria

def check_for_match(operator, needle, haystack):
    # print(needle.casefold())
    # print(haystack.casefold())
    if operator == 'eq' and needle == haystack:
        return True
    elif operator == 'eqi' and needle.casefold() == haystack.casefold():
        return True
    elif operator == 'ne' and needle != haystack:
        return True
    elif operator == 'nei' and needle.casefold() != haystack.casefold():
        return True
    elif operator == 'gt'and needle > haystack:
        return True
    elif operator == 'lt' and needle < haystack:
        return True
    elif operator == 'ge' and needle >= haystack:
        return True
    elif operator == 'le' and needle <= haystack:
        return True
    else:
        return False


def check_criteria(json_in, route_id, env):

    # For this route, get all rows with criteria
    tbl_dict = get_criteria.get_criteria(route_id, env)
    # print(tbl_dict)
    
    # crits_check_results structure...
    # { 
    #     grpkey1:
    #         {
    #             method: do_route | no_route,
    #             group_key: group_key,
    #             group_operator: 'OR',
    #             results: [
    #               {
    #                   field: PID-3,
    #                   found: True | False,
    #               },
    #               {
    #                   field: PID-2,
    #                   found: True | False,
    #               },
    #             ]
    #         },
    #     grpkey2: {...}
    # }
    crits_check_results = dict()

    # The major db entry to deal with is the field.
    # It has to be parsed out to compare against,
    # making note of the inclusion and/or absence of
    # repeating segments, elements or sub-elements.
    # the corresponding field from the data message.

    for f in tbl_dict:
        # print(f)
        f1 = f['field']
        f2 = f1.split("-")
        # print(f2)
        if "." in f2[1]:
            f3 = f2[1].split(".")
            sub_element = f3[1]
            # print('line71:'+str(f3))
        else:
            # print('line73:'+str(f2[1]))
            f3 = [f2[1], ''] #keep a 2 element dict for following check
            sub_element = None  # There is no sub_element in the target element.
            # print('line76:'+str(f3))

        if "[" in f2[0]:
            f4 = f2[0].split("[")
            segment = f4[0]
            seg_rep = f4[1][0]
        else:
            segment = f2[0]
            seg_rep = None  # The target segment does not repeat.
        # print('line85:'+str(f3))
        if "[" in f3[0]:
            f5 = f3[0].split("[")
            element = f5[0]
            ele_rep = f5[1][0]
        else:
            # print(str(f3[0]))
            element = f3[0]
            ele_rep = None  # The target element does not repeat.
            # print(str(element))

        #print("Segment is "+segment+", segment repeater is "+str(seg_rep)+", element is "+element+", element repeater is "+str(ele_rep)+", sub element is "+str(sub_element)+".")

        # The following code blocks tests if the message data matches any of the criteria in the
        # criteria database.
        json = dict()

        for (s, value) in json_in.items():
            if s.startswith(segment):
                json = json_in[s]
                break

        found_match = False

        if seg_rep is None and ele_rep is None and sub_element is None:
            found_match = check_for_match(f['operator'], f['value'], json[element].split("^")[0])

        elif seg_rep is None and ele_rep is None and sub_element is not None:
            sub_element = int(sub_element)
            sub_element = sub_element - 1
            found_match = check_for_match(f['operator'], f['value'], json[element].split("^")[sub_element])

        elif seg_rep is not None and ele_rep is None and sub_element is not None:
            seg_rep = int(seg_rep)
            sub_element = int(sub_element)
            sub_element = sub_element - 1
            found_match = check_for_match(f['operator'], f['value'], json[seg_rep][element].split("^")[sub_element])

        elif seg_rep is None and ele_rep is not None and sub_element is None:
            ele_rep = int(ele_rep)
            element = json[element].split("~")[ele_rep]
            found_match = check_for_match(f['operator'], f['value'], json[element].split("^")[0])

        elif seg_rep is None and ele_rep is not None and sub_element is not None:
            ele_rep = int(ele_rep)
            element = json[element].split("~")[ele_rep]
            sub_element = int(sub_element)
            sub_element = sub_element - 1
            found_match = check_for_match(f['operator'], f['value'], json[element].split("^")[sub_element])

        elif seg_rep is not None and ele_rep is not None and sub_element is not None:
            seg_rep = int(seg_rep)
            ele_rep = int(ele_rep)
            element = json[element].split("~")[ele_rep]
            sub_element = int(sub_element)
            sub_element = sub_element - 1
            found_match = check_for_match(f['operator'], f['value'], json[seg_rep][element].split("^")[sub_element])

        elif seg_rep is not None and ele_rep is None and sub_element is None:
            seg_rep = int(seg_rep)
            found_match = check_for_match(f['operator'], f['value'], json[seg_rep][element].split("^")[0])

        elif seg_rep is not None and ele_rep is not None and sub_element is None:
            seg_rep = int(seg_rep)
            ele_rep = int(ele_rep)
            element = json[element].split("~")[ele_rep]
            found_match = check_for_match(f['operator'], f['value'], json[seg_rep][element].split("^")[0])

        rd = dict(field=f['field'], found=found_match)
        group_key = f['group_key'] if len(f['group_key']) > 0 else 'empty'
        group_operator = f['group_operator'] if len(f['group_operator']) > 0 else 'empty'

        if group_key in crits_check_results:
            # already got one, so we are putting this iterations results in here only
            crits_check_results[group_key]['results'].append(rd)
        else:  # since group_key is empty, assume we grab all the 'empty' as our criteria list
            crits_check_results[group_key] = {'method': f['method'], 'group_key': group_key, 'group_operator': group_operator, 'results': [rd]}

    # Loop through result structure and determine return value, we output "false" BW does not route, we output "true" BW routes.

    # crits_check_results structure...
    # {
    #     grpkey1:
    #         {
    #             method: do_route | no_route,
    #             group_key: group_key,
    #             group_operator: 'OR',
    #             results: [
    #               {
    #                   field: PID-3,
    #                   found: True | False,
    #               },
    #               {
    #                   field: PID-2,
    #                   found: True | False,
    #               },
    #             ]
    #         },
    #     grpkey2: {...}
    # }

    for g_criteria_result in crits_check_results:
        grp_op = crits_check_results[g_criteria_result]['group_operator']
        grp_method = crits_check_results[g_criteria_result]['method']
        grp_res = "do_route" if grp_method == "do_route" else "no_route"
        # print(grp_res)
        # print(grp_op)
        # print(crits_check_results[g_criteria_result].get('results'))
        # print(type(crits_check_results[g_criteria_result].get('results')))
        found_test = [fr['found'] for fr in crits_check_results[g_criteria_result].get('results') if 'found' in fr]
        # print(found_test)

        if grp_op == 'AND':
            if False in found_test:
                if grp_method == "do_route":
                    grp_res = "no_route"
                else:
                    grp_res = "do_route"
        else:
            if True in found_test:
                if grp_method == "do_route":
                    grp_res = "do_route"
                else:
                    grp_res = "no_route"
            else:
                if grp_method == "no_route":
                    grp_res = "do_route"
                else:
                    grp_res = "no_route"

        if grp_res == "no_route":
            return "false"
    # we make it through all that we route
        return "true"
