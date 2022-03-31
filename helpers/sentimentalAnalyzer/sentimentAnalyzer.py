import pandas as pd
import pickle
from fileinput import filename
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.svm import SVC
from sklearn.metrics import make_scorer, accuracy_score
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from TurkishStemmer import TurkishStemmer


data = pd.read_excel("./urun.xlsx")
with open("./StopWordTurkce.txt", "r") as dosya:
    stop = dosya.read()


def text_preprocess(text):
    text = [word for word in (text.lower()).split() if word not in stop]
    return " ".join(text)


data['stop'] = data['Metin'].apply(text_preprocess)
kokbul = TurkishStemmer()


def stemming(text):
    words = word_tokenize(text)
    stems = []
    for w in words:
        stems.append(kokbul.stem(w))

    return ' '.join(stems)


data['stem'] = data['stop'].apply(stemming)
x = data['stem']
y = data['Durum']


x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42)
vectorizer = TfidfVectorizer()

vectorizer.fit(x_train)
training_features = vectorizer.transform(x_train)
test_features = vectorizer.transform(x_test)
parametreler = {'C': [1, 10, 100, 1000], 'kernel': ['linear', 'rbf'],
                'gamma': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
                }

acc_scorer = make_scorer(accuracy_score)

grid_obj = GridSearchCV(SVC(), parametreler, cv=10, scoring=acc_scorer)
grid_obj = grid_obj.fit(training_features, y_train)

model = grid_obj.best_estimator_
accuracy = grid_obj.best_score_
model.fit(training_features, y_train)
y_pred = model.predict(test_features)

print("Accuracy_score on the dataset:{:.2f}".format(
    accuracy_score(y_test, y_pred)))

filename = 'finalized_model.sav'
pickle.dump(model, open(filename, 'wb'))


def model_predict(trained_model, test_data):
    test_features = vectorizer.transform(test_data)
    return trained_model.predict(test_features)
