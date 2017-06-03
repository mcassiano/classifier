import itertools
import pandas as pd
from sklearn import model_selection
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.svm import LinearSVC

from stemming import tokenize
import matplotlib.pyplot as plt


def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = pd.np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, pd.np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, '%.2f' % cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.ylabel('True label')
    plt.xlabel('Predicted label')


angries = pd.read_csv('./newSet/angries.csv', dtype={'id': str, 'count': int, 'value': str})
hahas = pd.read_csv('./newSet/hahas.csv', dtype={'id': str, 'count': int, 'value': str})
loves = pd.read_csv('./newSet/loves.csv', dtype={'id': str, 'count': int, 'value': str})
sads = pd.read_csv('./newSet/sads.csv', dtype={'id': str, 'count': int, 'value': str})
wows = pd.read_csv('./newSet/wows.csv', dtype={'id': str, 'count': int, 'value': str})

angries = angries.sort_values(['count'], ascending=False)[0:304]
hahas = hahas.sort_values(['count'], ascending=False)[0:304]
loves = loves.sort_values(['count'], ascending=False)[0:281]
sads = sads.sort_values(['count'], ascending=False)[0:304]
wows = wows.sort_values(['count'], ascending=False)[0:304]

angries['class'] = 1
hahas['class'] = 2
loves['class'] = 3
sads['class'] = 4
wows['class'] = 5
#
# loves['class'] = 1
# sads['class'] = 2
# wows['class'] = 3

sw = open('stopwords.txt').read().split('\n')
df = angries.append(hahas)
df = df.append(loves)
df = df.append(sads)
df = df.append(wows)
###
# df = loves
# df = df.append(sads)
# df = df.append(wows)

count_vect = TfidfVectorizer(tokenizer=tokenize, stop_words=sw, strip_accents='ascii', ngram_range=(1, 2))
count_vect.fit(df['value'])

X = count_vect.transform(df['value'])
y = df['class']

X = X.toarray()

X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.3, random_state=0)

grid = GridSearchCV(LinearSVC(), param_grid={'C': [0.1, 1, 10, 100, 1000]})
grid.fit(X_train, y_train)
print("Best parameters set found on development set:")
print()
print(grid.best_params_)
print()
print("Grid scores on development set:")
print()
means = grid.cv_results_['mean_test_score']
stds = grid.cv_results_['std_test_score']
print("Detailed classification report:")
print()
print("The model is trained on the full development set.")
print("The scores are computed on the full evaluation set.")
print()
y_true, y_pred = y_test, grid.predict(X_test)
print(classification_report(y_true, y_pred, target_names=['angries', 'hahas', 'loves', 'sads', 'wows']))
print()

cnf_matrix = confusion_matrix(y_test, y_pred)
pd.np.set_printoptions(precision=2)
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=['angries', 'hahas', 'loves', 'sads', 'wows'], normalize=True,
                      title='Normalized confusion matrix')

plt.show()
