import json

fileDescriptor = open('posts.json', 'r')
postsJson = json.load(fileDescriptor)
posts = {}

for post in postsJson:
    posts[post['id']] = post

loves = open('data/loves.csv', 'r')
wows = open('data/wows.csv', 'r')
hahas = open('data/hahas.csv', 'r')
sads = open('data/sads.csv', 'r')
angries = open('data/angries.csv', 'r')

newDataset = open('data/multilabel.csv', 'w')
newDataset.write('label,text\n')

descriptors = [loves, wows, hahas, sads, angries]
count = 0

for i in range(0, len(descriptors)):
    descriptor = descriptors[i]
    for line in descriptor.readlines():
        splittedLine = line.split(',')
        facebookId = str(splittedLine[0])
        if 'id' in facebookId:
            continue

        post = posts[facebookId]
        reactions = post['reactions']
        reactionsCount = sum(reactions.values())
        if reactionsCount < 100:
            continue

        wowCount = reactions['wow'] / reactionsCount
        hahaCount = reactions['haha'] / reactionsCount
        angryCount = reactions['angry'] / reactionsCount
        loveCount = reactions['loves'] / reactionsCount
        sadCount = reactions['sad'] / reactionsCount

        reactions = post['reactions']
        sortedReactions = sorted(reactions, key=reactions.get, reverse=True)
        winner = sortedReactions[0]
        # line = '%s,%s,%f,%f,%f,%f,%f\n' % (splittedLine[0], splittedLine[2].replace("\n", ""),
        #                                    wowCount, hahaCount, angryCount,
        #                                    loveCount, sadCount)

        line = '%d,%s\n' % (ord(winner[0]), splittedLine[2].replace("\n", ""))
        print(line)
        newDataset.write(line)
        count += 1

print(count)
