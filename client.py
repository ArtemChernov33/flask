import requests


HOST = 'http://127.0.0.1:5000'

# response = requests.get(HOST)
# print(response.status_code)
# print(response.text)


response = requests.post(f'{HOST}/mails/', json={'header':'notification2', 'description':'You must submit on time HW', 'sender':'Prepod'})
print(response.status_code)
print(response.text)


# response = requests.patch(f'{HOST}/mails/1', json={'header':'notification_2'})
# print(response.status_code)
# print(response.text)

# response = requests.delete(f'{HOST}/mails/1')
# print(response.status_code)
# print(response.text)

response = requests.get(f'{HOST}/mails/2')
print(response.status_code)
print(response.text)