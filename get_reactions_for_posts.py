import json
from time import sleep

import requests


def parsePost(postDict):
    return {
        'id': postDict.get('id'),
        'message': postDict.get('message'),
        'link': postDict.get('link'),
        'reactions': {
            'loves': postDict.get('love').get('summary').get('total_count'),
            'wow': postDict.get('wow').get('summary').get('total_count'),
            'haha': postDict.get('haha').get('summary').get('total_count'),
            'sad': postDict.get('sad').get('summary').get('total_count'),
            'angry': postDict.get('angry').get('summary').get('total_count')
        }
    }


accessToken = 'EAABr0OtJzFcBAFZBLgtx4913DATa3mNcv' \
              'NZCJZCazALOh5dpCHsxUj1PkiWoPxSuAzNpg1jOCl9c1i' \
              'D69QO5uyg7xVCiMpMtGvUk5m8TRJZA1GCM7Sbyf4ZAUQVCZB' \
              'NE5i95a8sEQVwDnuvCNxRBdZA2uIe9sZAza0MZD'
fields = 'id,message,link,created_time,reactions.type(LOVE).summary(total_count).limit(0).as(love),reactions.type(WOW).summary(total_count).limit(0).as(wow),reactions.type(HAHA).summary(total_count).limit(0).as(haha),reactions.type(SAD).summary(total_count).limit(0).as(sad),reactions.type(ANGRY).summary(total_count).limit(0).as(angry)'
urlFormat = 'https://graph.facebook.com/v2.9/g1/posts?fields={0}&limit=100&access_token={1}'

url = urlFormat.format(fields, accessToken)
response = requests.get(url).json()

posts = []

for postDict in response['data']:
    posts.append(parsePost(postDict))

print "Page 0: ok."

for page in range(0, 200):
    nextPage = response['paging']['next']
    response = requests.get(nextPage).json()

    for postDict in response['data']:
        posts.append(parsePost(postDict))

    if page % 10 == 0:
        print "Sleeping for ten seconds."
        sleep(10)

    print "Page %d: ok." % (page + 1)

outFile = open('posts.json', 'w')
outFile.write(json.dumps(posts))
outFile.close()
