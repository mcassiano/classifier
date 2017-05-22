import pandas as pd
from sklearn import model_selection
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from stop_words import get_stop_words
from sklearn.neighbors import KNeighborsClassifier

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

df = angries.append(hahas)
df = df.append(loves)
df = df.append(sads)
df = df.append(wows)

# Data cleansing (sleuthing?)
df = df[df.value != '\\N']

count_vect = TfidfVectorizer(min_df=1, stop_words=get_stop_words('portuguese'), strip_accents='ascii')
count_vect.fit(df['value'])

X = count_vect.transform(df['value'])
y = df['class']

# clf = GaussianNB()
X = X.toarray()

X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.2, random_state=0)

k_folds = [5, 10]
gammas = [0.01, 0.1, 1, 10, 100, 1000]
# k_neighbors = [1, 2, 3, 4, 5, 6, 7, 8]
cs = [1, 10, 100, 1000]
params_svm_knn = {
    'rbf': [{'kernel': ['rbf'], 'gamma': gammas, 'C': cs}],
    'linear': [{'kernel': ['linear'], 'C': cs}],
    # 'knn': [{'n_neighbors': k_neighbors}],
}

score_history = []
scores = {}
for classifier, params in params_svm_knn.items():
    scores[classifier] = []

for k in k_folds:
    for classifier, params in params_svm_knn.items():

        if classifier != 'knn':
            clf = GridSearchCV(SVC(verbose=True), params, cv=k, scoring='accuracy', verbose=10)
            clf.fit(X_train, y_train)
        else:
            clf = GridSearchCV(KNeighborsClassifier(), params, cv=k)
            clf.fit(X_train, y_train)

        scores[classifier].append([clf.best_score_, k, clf.best_params_])
        score_history.append([k, clf.cv_results_])

best_rbf = max(scores['rbf'], key=lambda s: s[0])
best_linear = max(scores['linear'], key=lambda s: s[0])
# best_knn = max(scores['knn'], key=lambda s: s[0])
# best_poly = max(scores['poly'], key=lambda s: s[0])

lin = SVC(**best_linear[2]).fit(X_train, y_train)
# poly = SVC(**best_poly[2]).fit(X_train, y_train)
rbf = SVC(**best_rbf[2]).fit(X_train, y_train)
# knn = KNeighborsClassifier(**best_knn[2]).fit(X_train, y_train)

y_pred_lin = lin.predict(X_test)
# y_pred_knn = knn.predict(X_test)
y_pred_rbf = rbf.predict(X_test)

print(accuracy_score(y_test, y_pred_lin))
# print(accuracy_score(y_test, y_pred_knn))
print(accuracy_score(y_test, y_pred_rbf))
print(classification_report(y_test, y_pred_lin, target_names=['angries', 'hahas', 'loves', 'sads', 'wows']))
# print(classification_report(y_test, y_pred_knn, target_names=['angries', 'hahas', 'loves', 'sads', 'wows']))
print(classification_report(y_test, y_pred_rbf, target_names=['angries', 'hahas', 'loves', 'sads', 'wows']))
