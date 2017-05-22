import pandas as pd
from sklearn import model_selection
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.grid_search import GridSearchCV
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.naive_bayes import MultinomialNB

angries = pd.read_csv('./angries.csv')
hahas = pd.read_csv('./hahas.csv')
loves = pd.read_csv('./loves.csv')
sads = pd.read_csv('./sads.csv')
wows = pd.read_csv('./wows.csv')

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
df = df[df.value != '\\N']

count_vect = TfidfVectorizer(stop_words=sw, strip_accents='ascii')
count_vect.fit(df['value'])

X = count_vect.transform(df['value'])
y = df['class']

X = X.toarray()

X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.1)

text_clf = MultinomialNB()

text_clf.fit(X_train, y_train)
predicted_labels = text_clf.predict(X_test)

# rbf = SVC(verbose = True).fit(X_train, y_train)
# y_pred_rbf = rbf.predict(X_test)
print(accuracy_score(y_test, predicted_labels))
print(classification_report(y_test, predicted_labels, target_names=['angries', 'hahas', 'loves', 'sads', 'wows']))
