import json
from time import sleep

import re
import requests
import unicodedata

from bs4 import BeautifulSoup


def parsePost(postDict):
    return {
        'id': postDict.get('id'),
        'message': postDict.get('message'),
        'link': postDict.get('link'),
        'reactions': {
            'love': postDict.get('love').get('summary').get('total_count'),
            'wow': postDict.get('wow').get('summary').get('total_count'),
            'haha': postDict.get('haha').get('summary').get('total_count'),
            'sad': postDict.get('sad').get('summary').get('total_count'),
            'angry': postDict.get('angry').get('summary').get('total_count')
        }
    }


def clean_str(dirtyText):
    matcher = re.compile(r'<http.+?>', re.DOTALL)
    strippedUrls = re.sub(matcher, ' ', dirtyText)
    normalizedData = unicodedata.normalize('NFKD', strippedUrls)
    asciiDecoded = normalizedData.encode('ASCII', 'ignore').decode('ASCII')
    strippedHashtags = re.sub("#\S+", " ", asciiDecoded)
    strippedParenthesis = re.sub(r"\(.*\)", " ", strippedHashtags)
    strippedNewLines = strippedParenthesis.replace("\n", " ")
    onlyAlpha = re.sub('[^a-z A-Z]+', ' ', strippedNewLines)
    return onlyAlpha.strip().lower()


class DatasetBuilder:
    def __init__(self, filename):
        readDescriptor = open('%s.json' % filename, 'r')
        self.posts = json.load(readDescriptor)

    def build(self):
        descriptors = {}

        for post in self.posts:
            reactions = post['reactions']
            sortedReactions = sorted(reactions, key=reactions.get, reverse=True)
            predominant = sortedReactions[0]

            if predominant not in descriptors:
                descriptors[predominant] = open('data/%s.csv' % predominant, 'w')

            if post['message'] is not None and not any(c.isupper() for c in post['message']):
                descriptors[predominant].write(
                    post['id'] + ',' + str(reactions[predominant]) + ',' + post['message'] + '\n')


class FacebookPostsRetriever:
    fields = 'id,message,link,created_time,reactions.type(LIKE).summary(total_count).limit(0).as(like),' \
             'reactions.type(LOVE).summary(total_count).limit(0).as(love),' \
             'reactions.type(WOW).summary(total_count).limit(0).as(wow),' \
             'reactions.type(HAHA).summary(total_count).limit(0).as(haha),' \
             'reactions.type(SAD).summary(total_count).limit(0).as(sad),' \
             'reactions.type(ANGRY).summary(total_count).limit(0).as(angry)'

    urlFormat = 'https://graph.facebook.com/v2.9/{2}/posts?fields={0}&limit=100&access_token={1}'

    def __init__(self, accessToken, facebookPage, eligibilityThreshold=0.75):
        self.accessToken = accessToken
        self.facebookPage = facebookPage
        self.threshold = eligibilityThreshold

    def start(self, pageLimit):
        posts = []
        print("Page 1: processing.")
        url = self.urlFormat.format(self.fields, self.accessToken, self.facebookPage)
        response = requests.get(url).json()

        for postDict in response['data']:
            post = parsePost(postDict)
            if self.isEligibleByReactionCount(post):
                posts.append(post)

        print("Page 1: ok.")

        for page in range(1, pageLimit):
            print("Page %d: processing." % (page + 1))
            nextPage = response['paging']['next']
            response = requests.get(nextPage).json()

            for postDict in response['data']:
                post = parsePost(postDict)
                if self.isEligibleByReactionCount(post):
                    posts.append(post)

            if page % 10 == 0:
                print("Sleeping for two seconds.")
                sleep(2)

            print("Page %d: ok." % (page + 1))

        outFile = open('posts-' + self.facebookPage + '.json', 'w')
        outFile.write(json.dumps(posts))
        outFile.close()
        return posts

    def isEligibleByReactionCount(self, post):
        reactions = post['reactions']
        sortedReactions = sorted(reactions, key=reactions.get, reverse=True)
        reactionsCount = sum(reactions.values())

        if reactionsCount <= 10:
            return False

        return reactions[sortedReactions[0]] / reactionsCount > self.threshold


# noinspection PyBroadException
class PageScraper:
    def __init__(self, filename, filterFunction):
        self.filterFunction = filterFunction
        self.filename = filename

    def start(self):

        fileDescriptor = open('%s.json' % self.filename, 'r')
        posts = json.load(fileDescriptor)
        print("scraping %d posts" % len(posts))

        for post in posts:
            link = post['link']
            if link is None:
                continue

            message = self.scrape(link)

            if message is not None:
                post['message'] = message

        outFile = open(self.filename + '-scraped.json', 'w')
        outFile.write(json.dumps(posts))
        outFile.close()
        return posts

    def scrape(self, link):
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
            return None

        if self.filterFunction(response):
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

                if title is None:
                    title = u''
                if description is None and 'if gte mso 9' not in description:
                    description = u''

                message = clean_str(title) + ' ' + clean_str(description)

                if len(message) > 70:
                    print(message)
                    return message
        else:
            print("ignoring, does not match filter...")
            return None


def g1filter(response):
    if 'g1.globo.com' not in response.url:
        return False
    if '/politica/' in response.url:
        return False
    if 'globoesporte' in response.url:
        return False
    if 'autoesporte' in response.url:
        return False
    if '/ao-vivo/' in response.url:
        return False
    if '/agenda/' in response.url:
        return False
    if 'agenda-do-dia' in response.url:
        return False
    if 'resumo-do-dia' in response.url:
        return False
    if 'especiais.g1.globo.com' in response.url:
        return False
    if '/carros/' in response.url:
        return False
    return True


if __name__ == '__main__':
    token = 'EAABr0OtJzFcBAFZBLgtx4913DATa3mNcv' \
            'NZCJZCazALOh5dpCHsxUj1PkiWoPxSuAzNpg1jOCl9c1i' \
            'D69QO5uyg7xVCiMpMtGvUk5m8TRJZA1GCM7Sbyf4ZAUQVCZB' \
            'NE5i95a8sEQVwDnuvCNxRBdZA2uIe9sZAza0MZD'

    # retriever = FacebookPostsRetriever(token, 'g1')
    # retriever.start(200)
    # sleep(10)
    scraper = DatasetBuilder('posts-g1-scraped')
    scraper.build()
