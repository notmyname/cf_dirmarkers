#!/usr/bin/env python

import httplib

import cf_auth

CDN_LOGS = '.CDN_ACCESS_LOGS'

# auth
conn = httplib.HTTPSConnection('api.mosso.com')
conn.request('GET', '/auth', headers={'x-auth-user': cf_auth.username,
                                      'x-auth-key': cf_auth.apikey})
resp = conn.getresponse()
auth_token = resp.getheader('x-auth-token')
url = resp.getheader('x-storage-url')
conn.close()

# working in the same contianer
container_path = '/' + '/'.join(url.split('/')[3:]) + '/' + CDN_LOGS

# use one connection to avoid setup/teardowns
conn = httplib.HTTPSConnection(url.split('/')[2])


def get_listing(marker=None):
    global conn
    query = container_path
    if marker:
        query += '?marker=%s' % marker
    conn.request('GET', query, headers={'X-Auth-Token': auth_token})
    resp = conn.getresponse()
    return [x for x in resp.read().split('\n') if x]

# find all the unique prefixes
prefixes = set()
results = ['foo']
last = None
while len(results):
    results = get_listing(marker=last)
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

# create the directory markers
send_headers = {'X-Auth-Token': auth_token,
                'Content-Type': 'application/directory'}
container_path = '/' + '/'.join(url.split('/')[3:]) + '/' + CDN_LOGS
print len(prefixes), 'objects to create'
for i, p in enumerate(sorted(prefixes)):
    conn.request('PUT', container_path + '/' + p, headers=send_headers)
    conn.getresponse().read()
    print i
