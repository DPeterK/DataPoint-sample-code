import datapoint_access as dpa

api_key = str(raw_input('Please enter a valid API Key: '))

url1 = dpa.DPRequest('val', 'wxobs', api_key, site_id=3772, res='hourly')
url1.build_request()
data1 = url1.parse_response()

print('Response {}\n'.format(url1.response))
print('Parsed data: {}\n'.format(data1))

# As can be seen, actually getting to the numbers can prove interesting:
numbers = data1['SiteRep']['DV']['Location']['Period']
pressure = []
for number in numbers:
    itms = number['Rep']
    for itm in itms:
        pressure.append(itm['P'])
print('Retrieved pressure data:\n{}'.format(pressure))
