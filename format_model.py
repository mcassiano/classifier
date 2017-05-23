# -*- coding: utf-8 -*-
import json
import re

import requests
from bs4 import BeautifulSoup
import unicodedata


def clean_str(message2):
    message1 = unicodedata.normalize('NFKD', message2).encode('ASCII', 'ignore').decode('ASCII')
    message1 = re.sub(r"\(.*\)", "", message1)
    message1 = re.sub("#\S+", "", message1)
    message1 = re.sub(
        r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))',
        '', message1)
    message1 = message1.replace("\n", "")
    message1 = message1.replace("'", "")
    message1 = message1.replace("\"", "")
    message1 = message1.replace(",", "")
    message1 = message1.replace(";", "")
    message1 = message1.replace(".", "")
    message1 = message1.replace(":", "")
    message1 = message1.replace("-", " ")
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", message1)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()


loves = open('loves.csv', 'w')
loves.write('value\n')

wows = open('wows.csv', 'w')
wows.write('value\n')

hahas = open('hahas.csv', 'w')
hahas.write('value\n')

sads = open('sads.csv', 'w')
sads.write('value\n')

angries = open('angries.csv', 'w')
angries.write('value\n')

fileDescriptor = open('posts.json', 'r')
posts = json.load(fileDescriptor)
count = 0

descriptors = {"wow": wows, "haha": hahas,
               "angry": angries, "loves": loves,
               "sad": sads}

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
        except:
            print('retrying request...')
            response = None

    if response is None:
        print('max retries reached, skipping...')

    if 'g1.globo.com' not in response.url:
        continue
    if 'globoesporte' in response.url:
        continue
    if 'autoesporte' in response.url:
        continue
    if '/ao-vivo/' in response.url:
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
        message = u'%s %s'

        if title is None:
            title = u''
        if descriptors is None:
            description = u''

        message %= clean_str(title), clean_str(description)

        if len(message) < 70:
            continue

        print("Writing message: %s." % message)
        reactions = post['reactions']
        sortedKeys = sorted(reactions, key=reactions.get, reverse=True)
        predominantReaction = sortedKeys[0]
        if reactions[predominantReaction] > 0:
            print("Reaction chosen: %s" % predominantReaction)
            descriptors[predominantReaction].write(message + "\n")
            count += 1

print('%d items processed' % count)

loves.close()
wows.close()
hahas.close()
sads.close()
angries.close()
