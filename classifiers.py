from numpy import mean
from numpy import std
from sklearn import model_selection
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier, \
    AdaBoostClassifier, \
    GradientBoostingClassifier

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.grid_search import GridSearchCV


class EstimatorSelectionHelper:
    def __init__(self, models, params):
        if not set(models.keys()).issubset(set(params.keys())):
            missing_params = list(set(models.keys()) - set(params.keys()))
            raise ValueError("Some estimators are missing parameters: %s" % missing_params)
        self.models = models
        self.params = params
        self.keys = models.keys()
        self.grid_searches = {}

    def fit(self, X, y, cv=3, n_jobs=1, verbose=10, scoring=None, refit=False):
        for key in self.keys:
            print("Running GridSearchCV for %s." % key)
            model = self.models[key]
            params = self.params[key]
            gs = GridSearchCV(model, params, cv=cv, n_jobs=n_jobs,
                              verbose=verbose, scoring=scoring, refit=refit)
            gs.fit(X, y)
            self.grid_searches[key] = gs

    def score_summary(self, sort_by='mean_score'):
        def row(key, scores, params):
            d = {
                'estimator': key,
                'min_score': min(scores),
                'max_score': max(scores),
                'mean_score': mean(scores),
                'std_score': std(scores),
            }
            return pd.Series(dict(params.items() + d.items()))

        rows = [row(k, gsc.cv_validation_scores, gsc.parameters)
                for k in self.keys
                for gsc in self.grid_searches[k].grid_scores_]
        df = pd.concat(rows, axis=1).T.sort([sort_by], ascending=False)

        columns = ['estimator', 'min_score', 'mean_score', 'max_score', 'std_score']
        columns += [c for c in df.columns if c not in columns]

        return df[columns]


models1 = {
    'ExtraTreesClassifier': ExtraTreesClassifier(),
    'RandomForestClassifier': RandomForestClassifier(),
    # 'AdaBoostClassifier': AdaBoostClassifier(),
    'GradientBoostingClassifier': GradientBoostingClassifier(),
}

params1 = {
    'ExtraTreesClassifier': {'n_estimators': [16, 32]},
    'RandomForestClassifier': {'n_estimators': [16, 32]},
    # 'AdaBoostClassifier': {'n_estimators': [16, 32]},
    'GradientBoostingClassifier': {'n_estimators': [16, 32], 'learning_rate': [0.8, 1.0]},
}

angries = pd.read_csv('./angries1.csv')
hahas = pd.read_csv('./hahas1.csv')
loves = pd.read_csv('./loves1.csv')
sads = pd.read_csv('./sads1.csv')
wows = pd.read_csv('./wows1.csv')

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
df = df[df.value = '\\N']

count_vect = TfidfVectorizer(stop_words=sw, strip_accents='ascii')
count_vect.fit(df['value'])

X = count_vect.transform(df['value'])
y = df['class']

X = X.toarray()

X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.2)

helper1 = EstimatorSelectionHelper(models1, params1)
helper1.fit(X_train, y_train, scoring='f1', n_jobs=-1)
