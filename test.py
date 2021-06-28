import requests
import json
page = 1
url = 'https://api.managebac.com/v2/classes/11468717/tasks/26425174'
headers = {'auth-token': 'ff9ea6a0c31a1e67ebf561754e2153e13c5fcb1760009528155bca7faa91b226'}
y = requests.get(url, headers=headers)
grades = json.loads(y.text)
print(grades)
for item in grades['students']:
    if any( x == 'criteria' for x in item['assessments'] ):
        for item2 in item['assessments']['criteria']:
            a = item2['label']
            print (a)
 

