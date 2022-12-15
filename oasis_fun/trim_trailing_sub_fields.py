def trim_trailing_sub_fields(json_in):
    for (s, value) in json_in.items():
        for (i, e) in json_in[s].items():
            n = e
            while n.endswith('^'):
                n = n[:-1]
            # print(i)
            # print(e)
            # print(n)
            json_in[s].update({i:n})
    return json_in
