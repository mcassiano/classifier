import pandas as pd
from sklearn import model_selection
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.svm import LinearSVC

angries = pd.read_csv('./data/angries.csv')
hahas = pd.read_csv('./data/hahas.csv')
loves = pd.read_csv('./data/loves.csv')
sads = pd.read_csv('./data/sads.csv')
wows = pd.read_csv('./data/wows.csv')

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

count_vect = TfidfVectorizer(stop_words=sw, strip_accents='ascii')
count_vect.fit(df['value'])

X = count_vect.transform(df['value'])
y = df['class']

X = X.toarray()

X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.2)
model = LinearSVC()
model.fit(X_train, y_train)
pred = model.predict(X_test)
print(classification_report(y_test, pred, target_names=['angries', 'hahas', 'loves', 'sads', 'wows']))
