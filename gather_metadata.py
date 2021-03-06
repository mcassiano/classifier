import json

fileDescriptor = open('posts.json', 'r')
posts = json.load(fileDescriptor)
newPosts = {}

for post in posts:
    newPosts[post['id']] = post

loves = open('data/loves.csv', 'r')
wows = open('data/wows.csv', 'r')
hahas = open('data/hahas.csv', 'r')
sads = open('data/sads.csv', 'r')
angries = open('data/angries.csv', 'r')

newLoves = open('newSet/loves.csv', 'w')
newWows = open('newSet/wows.csv', 'w')
newHahas = open('newSet/hahas.csv', 'w')
newSads = open('newSet/sads.csv', 'w')
newAngries = open('newSet/angries.csv', 'w')

descriptors = [loves, wows, hahas, sads, angries]
newDescriptors = [newLoves, newWows, newHahas, newSads, newAngries]

for i in range(0, len(descriptors)):
    descriptor = descriptors[i]
    for line in descriptor.readlines():
        splittedLine = line.split(',')
        facebookId = str(splittedLine[0])
        if 'id' in facebookId:
            newDescriptors[i].write(line)
            continue

        post = newPosts[facebookId]
        reactions = post['reactions']
        sortedReactions = sorted(reactions, key=reactions.get, reverse=True)
        reactionsCount = sum(reactions.values())
        threshold = 0.75

        if reactionsCount < 10:
            continue

        if reactions[sortedReactions[0]] / reactionsCount < threshold:
            continue

        newDescriptors[i].write(splittedLine[0] + ',' + splittedLine[1] + ',' + splittedLine[2])

for newDescriptor in newDescriptors:
    newDescriptor.close()
