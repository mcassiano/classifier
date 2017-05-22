from time import sleep

import requests

accessToken = 'EAABr0OtJzFcBAFZBLgtx4913DATa3mNcv' \
              'NZCJZCazALOh5dpCHsxUj1PkiWoPxSuAzNpg1jOCl9c1i' \
              'D69QO5uyg7xVCiMpMtGvUk5m8TRJZA1GCM7Sbyf4ZAUQVCZB' \
              'NE5i95a8sEQVwDnuvCNxRBdZA2uIe9sZAza0MZD'
fields = 'id,message,link,reactions.type(LOVE).summary(total_count).limit(0).as(love),reactions.type(WOW).summary(total_count).limit(0).as(wow),reactions.type(HAHA).summary(total_count).limit(0).as(haha),reactions.type(SAD).summary(total_count).limit(0).as(sad),reactions.type(ANGRY).summary(total_count).limit(0).as(angry)'
urlFormat = 'https://graph.facebook.com/v2.9/g1/posts?fields={0}&limit=100&access_token={1}'

url = urlFormat.format(fields, accessToken)
response = requests.get(url).json()
outFile = open('posts.txt', 'w')

for post in response['data']:
    outFile.write(post['id'] + '\n')

print "Page 0: ok."

for page in range(0, 300):
    nextPage = response['paging']['next']
    response = requests.get(nextPage).json()
    for post in response['data']:
        outFile.write(post['id'] + '\n')

    if page % 10 == 0:
        print "Sleeping for two seconds."
        sleep(2)

    print "Page %d: ok." % page

outFile.close()
