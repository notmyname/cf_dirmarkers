#!/usr/bin/env python

import httplib
import cloudfiles

import cf_auth

CDN_LOGS = '.CDN_ACCESS_LOGS'

conn = cloudfiles.get_connection(username=cf_auth.username,
                                 api_key=cf_auth.apikey)


prefixes = set()
container = conn.get_container(CDN_LOGS)
last = None
results = ['foo']
while len(results):
    results = container.list_objects(marker=last)
    if not results:
        break
    last = results[-1]
    for r in results:
        parts = r
        while parts:
            if '/' not in parts:
                break
            parts = parts.rsplit('/', 1)[0]
            if parts not in results:
                prefixes.add(parts)

url, _, auth_token = conn.auth.authenticate()
httpconn = httplib.HTTPSConnection(url.split('/')[2])
send_headers = {'X-Auth-Token': auth_token, 'Content-Type': 'application/directory'}
container_path = '/' + '/'.join(url.split('/')[3:]) + '/' + CDN_LOGS
print len(prefixes), 'objects to create'
for i, p in enumerate(sorted(prefixes)):
    httpconn.request('PUT', container_path+'/'+p, headers=send_headers)
    httpconn.getresponse().read()
    print i
