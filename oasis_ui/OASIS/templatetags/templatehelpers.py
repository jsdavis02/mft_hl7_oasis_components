from django import template

register = template.Library()


@register.simple_tag
def relative_url(value, field_name, urlencode=None, filter_url=True, remove_key=None):
    url = '?{}={}'.format(field_name, value)
    # print(url)
    if urlencode:
        querystring = urlencode.split('&')
        # print(str(querystring))
        filtered_querystring = querystring
        if filter_url:
            filtered_querystring = filter(lambda p: p.split('=')[0] != field_name, querystring)
            #print(type(filtered_querystring))
            if remove_key is not None:
                nl = []
                for f in filtered_querystring:
                    if remove_key not in f:
                       nl.append(f)
                filtered_querystring = nl
        # print(str(filtered_querystring))
        encoded_querystring = '&'.join(filtered_querystring)
        url = '{}&{}'.format(url, encoded_querystring)
    return url


@register.filter(name='get_dict_item')
def get_dict_item(dictionary, key):
    return dictionary.get(key)
