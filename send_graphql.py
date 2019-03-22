import requests

import config


def send_query(service, query_string):
    url = getattr(config, service)
    headers = {'Content-type': 'application/json'}
    r = requests.post(url, headers=headers, data=query_string)
    print(r.text[0:32])
    if r.status_code == 200:
        if r.text[0:31] == '{"data":{"sendMail":{"ok":true,':
            return r.text
        else:
            raise Exception("GraphQL query error: %s" % (r.text, ))
    else:
        raise Exception("Query failed to run with status code %s %s" % (r.status_code, r.text))
