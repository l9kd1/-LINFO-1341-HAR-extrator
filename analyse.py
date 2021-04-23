"""
Written by Loic Grumiaux - 37871800
April 2021

This website helped a great deal:
https://roymartinez.dev/2019-06-05-har-analysis/

"""
import json, os,re
import pandas as pd

directory = os.getcwd()+'/'

# CHANGE PARAMETERS BELOW

#  Le chemin vers le .har à partir du répertoire du script python
logname = 'inginious.har'
#  Le nom de domaine du site
analysed_domains = ['inginious.info.ucl.ac.be']

with open(directory+logname, 'r',encoding="utf-8") as f:
    har = json.loads(f.read())
    f.close()

def findHeader(req,headertype,headername,op = None):
    value = "None"
    if headertype == 'response' or headertype=='request':
        for h in req[headertype]['headers']:
            if op == 'in':
                if headername in h['name']:
                    value = h['value']
                    break
            else:
                if headername == h['name']:
                    value = h['value']
                    break

    if headertype == 'cdn-timing':
        value = 0
        for h in req['response']['headers']:
            if op == 'eq':
                if 'server-timing' in h['name']:
                    if headername in h['value']:

                        value = int(h['value'].split(';')[1].split('=')[1])
                        break
        if value is None:
            return 0
    return value

colmms = ['url',
        'host',
        'host-type',
        'httpVersion',
        'method',
        'status',
        'port_used',
        'ext',
        'server',
        'size_snt',
        'size_rcv']
dat_clean = pd.DataFrame(columns=colmms)
for r in har['log']['entries']:
    u = str(r['request']['url']).split('?')[0]
    if(r['response']['status']==0):
        continue
    host = re.search('://(.+?)/', u, re.IGNORECASE).group(0).replace(':','').replace('/','')


    cachekey = str(findHeader(r,'response','x-cache-key','eq'))
    if not cachekey == 'None':
        cachekey = cachekey.split('/')
        cpcode = int(cachekey[3])
        ttl = cachekey[4]
        cdnCache = str(findHeader(r,'response','x-cache','eq')).split(' ')[0]
        cdnCacheParent = str(findHeader(r,'response','x-cache-remote','eq')).split(' ')[0]
        origin = str(findHeader(r,'response','x-cache-key','eq')).split('/')[5]
    else:
        cachekey = "None"
        cpcode = "None"
        ttl = "None"
        cdnCache = "None"
        cdnCacheParent = "None"
        origin = "None"

    ext = re.search(r'(\.[A-Za-z0-9]+$)', u, re.IGNORECASE)
    if any(tld in host for tld in analysed_domains):
        hostType = 'First Party'
    else:
        hostType = 'Third Party'

    if ext is None:
        ext = "None"
    else:
        ext = ext.group(0).replace('.','')

    send_sz = findHeader(r,'request','Content-Length','eq')
    if(send_sz== "None"):
        send_sz=r['request'].get('content',{}).get('size','0')

    rcv_sz = findHeader(r,'response','Content-Length','eq')
    if(rcv_sz== "None"):
        rcv_sz=r['response'].get('content',{}).get('size','0')

    try:
        new_row = {
            'url':u,
            'host':host,
            'host-type':hostType,
            'httpVersion':r['request']['httpVersion'],
            'method':r['request']['method'],
            'status':r['response']['status'],
            'content-length':(float(rcv_sz)+float(send_sz))/1024,
            'port_used':r.get('connection','0'),
            'extension':ext,
            'server':str(findHeader(r,'response','server','eq')),
            'size_snt':((float(send_sz)+(r['request']['headersSize'] or 0))/(1024)),
            'size_rcv':((float(rcv_sz)+(r['response']['headersSize'] or 0))/(1024))
            }

        dat_clean = dat_clean.append(new_row,ignore_index=True)
    except Exception as e:
        print("Non standard http request encountered url:")
        print(u)
        print(str(e))
        print()

# Stats based on the aggregation of fields

agg_based_stats = [
    {
        "groupby":['host','url'],
        "sortby":['host',"Size received from host [KB]"],
        "aggfield":'size_rcv',
        "csv_name":"input_traffic_all_urls",
        "field":"Size received from host [KB]"
    },
    {
        "groupby":['host','url'],
        "sortby":['host',"Size sent to host [KB]"],
        "aggfield":'size_snt',
        "csv_name":"output_traffic_all_urls",
        "field":"Size sent to host [KB]"
    },
    {
        "groupby":['host'],
        "sortby":["Size received from host [KB]"],
        "aggfield":'size_rcv',
        "csv_name":"input_traffic_host",
        "field":"Size received from host [KB]"
    },
    {
        "groupby":['host'],
        "sortby":["Size sent to host [KB]"],
        "aggfield":'size_snt',
        "csv_name":"output_traffic_host",
        "field":"Size sent to host [KB]"
    },
    {
        "groupby":['extension'],
        "sortby":["Size received [KB]"],
        "aggfield":'content-length',
        "csv_name":"type_size",
        "field":"Size received [KB]"
    },
]

for param in agg_based_stats:
    tmp = dat_clean
    tmp = tmp.groupby(param["groupby"])[param["aggfield"]].agg('sum').reset_index(name=param["field"])
    tmp = tmp.sort_values(by=param["sortby"],ascending=False)
    tmp.to_csv(directory+'/'+param["csv_name"]+'.csv',index=False)
    print("*"*10)
    print(tmp)

    del tmp


# Stats based on the number of requests

size_based_stats = [
    {
        "groupby":['port_used'],
        "csv_name":"port_used"
    },
    {
        "groupby":['httpVersion','host'],
        "csv_name":"httpVersion_by_host"
    },
    {
        "groupby":['httpVersion'],
        "csv_name":"httpVersion"
    },
    {
        "groupby":['host','extension'],
        "csv_name":"type_data_host"
    },
    {
        "groupby":['extension'],
        "csv_name":"type_data"
    },
    {
        "groupby":['method'],
        "csv_name":"method_used"
    },
    {
        "groupby":['host','url'],
        "csv_name":"nb_url_perhost"
    }
]

field = "Requests"

for param in size_based_stats:
    tmp = dat_clean
    tmp = tmp.groupby(param["groupby"]).size().reset_index(name=field)

    tmp = tmp.sort_values(by=[field],ascending=False)
    tmp.to_csv(directory+'/'+param["csv_name"]+'.csv',index=False)
    print("*"*10)
    print(tmp)

    del tmp
