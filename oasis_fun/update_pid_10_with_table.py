# Function performs a db lookup to determine the
# value of PID 10 Patient Race by looking up the code based on inbound


from oasis_fun import get_codetable


def update_pid_10_with_table(json_in, key, env):


    tbl_dict = get_codetable.get_codetable(key, env)
    for (s, value) in json_in.items():
        if s.startswith('PID'):

            for d in tbl_dict:
                if d['input'] == json_in[s]['10']:
                    json_in[s].update({'10': d['output']})
                    break


    return json_in
