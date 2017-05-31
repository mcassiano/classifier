import itertools

import nltk
import pandas as pd
from nltk.stem.snowball import PortugueseStemmer
from sklearn import model_selection
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from nltk.stem.porter import *
# import matplotlib.pyplot as plt
from sklearn.svm import SVC

portugueseStemmer = PortugueseStemmer()


def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed


def tokenize(text):
    tokens = nltk.word_tokenize(text, 'portuguese')
    stems = stem_tokens(tokens, portugueseStemmer)
    return stems


# def plot_confusion_matrix(cm, classes,
#                           normalize=False,
#                           title='Confusion matrix',
#                           cmap=plt.cm.Blues):
#     """
#     This function prints and plots the confusion matrix.
#     Normalization can be applied by setting `normalize=True`.
#     """
#     plt.imshow(cm, interpolation='nearest', cmap=cmap)
#     plt.title(title)
#     plt.colorbar()
#     tick_marks = pd.np.arange(len(classes))
#     plt.xticks(tick_marks, classes, rotation=45)
#     plt.yticks(tick_marks, classes)
#
#     if normalize:
#         cm = cm.astype('float') / cm.sum(axis=1)[:, pd.np.newaxis]
#         print("Normalized confusion matrix")
#     else:
#         print('Confusion matrix, without normalization')
#
#     print(cm)
#
#     thresh = cm.max() / 2.
#     for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
#         plt.text(j, i, cm[i, j],
#                  horizontalalignment="center",
#                  color="white" if cm[i, j] > thresh else "black")
#
#     plt.tight_layout()
#     plt.ylabel('True label')
#     plt.xlabel('Predicted label')


angries = pd.read_csv('./newSet/angries.csv', dtype={'id': str, 'count': int, 'value': str})
hahas = pd.read_csv('./newSet/hahas.csv', dtype={'id': str, 'count': int, 'value': str})
loves = pd.read_csv('./newSet/loves.csv', dtype={'id': str, 'count': int, 'value': str})
sads = pd.read_csv('./newSet/sads.csv', dtype={'id': str, 'count': int, 'value': str})
wows = pd.read_csv('./newSet/wows.csv', dtype={'id': str, 'count': int, 'value': str})

angries = angries.sort_values(['count'], ascending=False)[0:1800]
hahas = hahas.sort_values(['count'], ascending=False)[0:1800]
loves = loves.sort_values(['count'], ascending=False)[0:1800]
sads = sads.sort_values(['count'], ascending=False)[0:1800]
wows = wows.sort_values(['count'], ascending=False)[0:1800]

angries['class'] = 1
hahas['class'] = 2
loves['class'] = 3
sads['class'] = 4
wows['class'] = 5

sw = open('stopwords.txt').read().split('\n')
df = angries.append(hahas)
df = df.append(loves)
df = df.append(sads)
df = df.append(wows)

count_vect = TfidfVectorizer(tokenizer=tokenize, stop_words=sw)
count_vect.fit(df['value'])

X = count_vect.transform(df['value'])
y = df['class']

X = X.toarray()

X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.05)

# Set the parameters by cross-validation
tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4],
                     'C': [1, 10, 100, 1000]},
                    {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]

scores = ['precision', 'recall']

for score in scores:
    print("# Tuning hyper-parameters for %s" % score)
    print()

    clf = GridSearchCV(SVC(C=1), tuned_parameters, cv=5,
                       scoring='%s_macro' % score)
    clf.fit(X_train, y_train)

    print("Best parameters set found on development set:")
    print()
    print(clf.best_params_)
    print()
    print("Grid scores on development set:")
    print()
    means = clf.cv_results_['mean_test_score']
    stds = clf.cv_results_['std_test_score']
    for mean, std, params in zip(means, stds, clf.cv_results_['params']):
        print("%0.3f (+/-%0.03f) for %r"
              % (mean, std * 2, params))
    print()

    print("Detailed classification report:")
    print()
    print("The model is trained on the full development set.")
    print("The scores are computed on the full evaluation set.")
    print()
    y_true, y_pred = y_test, clf.predict(X_test)
    print(classification_report(y_true, y_pred))
    print()

#
# cnf_matrix = confusion_matrix(y_test, pred)
# pd.np.set_printoptions(precision=2)
#
# # Plot non-normalized confusion matrix
# plt.figure()
# plot_confusion_matrix(cnf_matrix, classes=['angries', 'hahas', 'loves', 'sads', 'wows'],
#                       title='Confusion matrix, without normalization')
#
# # Plot normalized confusion matrix
# plt.figure()
# plot_confusion_matrix(cnf_matrix, classes=['angries', 'hahas', 'loves', 'sads', 'wows'], normalize=True,
#                       title='Normalized confusion matrix')
#
# plt.show()
