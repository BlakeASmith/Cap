from requests import post
from cap.store.textobjects import Line

SERVER_URL = 'http://127.0.0.1:5000'
TESTLIST = 'testlist'

response = post(SERVER_URL+f'/create/Line/{TESTLIST}')
print(response.text)

added = post(SERVER_URL+f'/add/{TESTLIST}', json={
        'items':[
                'line 1',
                'line 2',
                'line 3' 
            ]
    })

print(added.text)

removed = post(SERVER_URL+f'/remove/{TESTLIST}', json={
        'items':[
                'line 1',
                'line 2',
                'line 3' 
            ]
    })

print(removed.text)

deleted = post(SERVER_URL+f'/delete/{TESTLIST}')
print(deleted.text)


