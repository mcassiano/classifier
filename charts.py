import json
from random import random

import itertools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

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

descriptors = [loves, wows, hahas, sads, angries]
samples = {}


def random_jitter(y):
    return y + random() * 0.4


def plot(xs, ys, labels):
    colors = cm.rainbow(np.linspace(0, 1, len(ys)))
    area = np.pi * 20
    fig, ax = plt.subplots()
    markers = itertools.cycle(('D', ',', 'v', 'o', 'p'))

    for x, y, c, label, marker in zip(xs, ys, colors, labels, markers):
        x = list(map(random_jitter, x))
        y = list(map(random_jitter, y))
        ax.scatter(x, y, edgecolors=c, marker=marker,
                   facecolors='none', linewidth='2', s=area, alpha=0.5, label=label)

    ax.legend()
    ax.grid(True)
    plt.show()


for i in range(0, len(descriptors)):
    descriptor = descriptors[i]
    for line in descriptor.readlines():
        splittedLine = line.split(',')
        facebookId = str(splittedLine[0])
        if 'id' in facebookId:
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

        percentage = reactions[sortedReactions[0]] / reactionsCount

        if samples.get(sortedReactions[0]):
            if len(samples[sortedReactions[0]]) < 200:
                samples[sortedReactions[0]].append(percentage)
        else:
            samples[sortedReactions[0]] = [percentage]

xs = []
ys = []
labels = []
i = 0
for key, reactionSamples in samples.items():
    x = []
    y = []
    for j in range(0, len(reactionSamples)):
        xNoise = random() * 0.1 + reactionSamples[j]
        yNoise = i + 2

        x.append(xNoise)
        y.append(yNoise)

    xs.append(x)
    ys.append(y)
    labels.append(key)

    i += 1

plot(xs, ys, labels)
