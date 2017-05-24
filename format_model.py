# -*- coding: utf-8 -*-
import json
import re
from string import punctuation
from time import sleep

import requests
from bs4 import BeautifulSoup
import unicodedata


def clean_str(dirtyText):
    matcher = re.compile(r'<http.+?>', re.DOTALL)
    strippedUrls = re.sub(matcher, '', dirtyText)
    normalizedData = unicodedata.normalize('NFKD', strippedUrls)
    asciiDecoded = normalizedData.encode('ASCII', 'ignore').decode('ASCII')
    strippedHashtags = re.sub("#\S+", "", asciiDecoded)
    strippedParenthesis = re.sub(r"\(.*\)", "", strippedHashtags)
    strippedNewLines = strippedParenthesis.replace("\n", " ")
    onlyAlpha = re.sub('[^a-z A-Z]+', '', strippedNewLines)
    return onlyAlpha.strip().lower()


loves = open('data/loves.csv', 'w')
loves.write('id,count,value\n')

wows = open('data/wows.csv', 'w')
wows.write('id,count,value\n')

hahas = open('data/hahas.csv', 'w')
hahas.write('id,count,value\n')

sads = open('data/sads.csv', 'w')
sads.write('id,count,value\n')

angries = open('data/angries.csv', 'w')
angries.write('id,count,value\n')

fileDescriptor = open('posts.json', 'r')
posts = json.load(fileDescriptor)
count = 0

descriptors = {"wow": wows, "haha": hahas,
               "angry": angries, "loves": loves,
               "sad": sads}


def closeFiles():
    loves.close()
    wows.close()
    hahas.close()
    sads.close()
    angries.close()


for post in posts:
    link = post['link']
    if link is None:
        continue

    print('requesting %s' % link)
    response = None
    retries = 0
    while response is None:
        try:
            if retries == 5:
                break
            retries += 1
            response = requests.get(link)
        except KeyboardInterrupt:
            closeFiles()
        except:
            print('retrying request...')
            response = None

    if response is None:
        print('max retries reached, skipping...')
        continue

    if 'g1.globo.com' not in response.url:
        continue
    if 'globoesporte' in response.url:
        continue
    if 'autoesporte' in response.url:
        continue
    if '/ao-vivo/' in response.url:
        continue
    if '/agenda/' in response.url:
        continue

    print(response.url)
    soup = BeautifulSoup(response.text, "lxml")

    title = soup.find(attrs={'name': 'title'})
    if title is None:
        title = soup.find(attrs={'itemprop': 'name'})

    description = soup.find(attrs={'name': 'description'})
    if description is None:
        description = soup.find(attrs={'itemprop': 'description'})

    if title is not None:
        title = title.get('content')

    if description is not None:
        description = description.get('content')

    if title is not None or description is not None:
        message = u''

        if title is None:
            title = u''
        if descriptors is None:
            description = u''

        message = clean_str(title) + ' ' + clean_str(description)

        if len(message) < 70:
            continue

        print("Writing message: %s" % message)
        reactions = post['reactions']
        sortedKeys = sorted(reactions, key=reactions.get, reverse=True)
        predominantReaction = sortedKeys[0]
        if reactions[predominantReaction] > 0:
            print("Reaction chosen: %s" % predominantReaction)
            descriptors[predominantReaction].write(
                post['id'] + ',' + str(reactions[predominantReaction]) + ',' + message + "\n")
            count += 1

print('%d items processed' % count)
closeFiles()
