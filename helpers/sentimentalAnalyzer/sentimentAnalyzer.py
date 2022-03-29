from nltk.tokenize import word_tokenize
from sklearn.metrics import make_scorer, accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import cross_val_score, cross_validate
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import os
import seaborn as sns
import numpy as np  # linear algebra
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
import matplotlib.pyplot as plt
from TurkishStemmer import TurkishStemmer
import nltk
nltk.download('punkt')

data = pd.read_excel('C:\\Users\\EbubekirPC\\Desktop\\s\\TrkceTwit.xlsx')

with open("C:\\Users\\EbubekirPC\\Desktop\\s\\StopWordTurkce.txt", "r") as dosya:
    stop = dosya.read()


def text_preprocess(text):
    """
    Her boşlukta metini parçaya ayır ve bu parça eğer stopwords dosyasında yoksa bunu,
    geri döndürülecek metin içeriğine ekle.
    """
    text = [word for word in text.split() if word not in stop]
    return " ".join(text)


data['stop'] = data['Tweets'].apply(text_preprocess)
kokbul = TurkishStemmer()


def stemming(text):
    """
    Parçalanmış kelimelerin her birisini köklerine ayırıyor.
    """
    words = word_tokenize(text)
    stems = []

    for w in words:
        stems.append(kokbul.stem(w))

    return ' '.join(stems)


data['stemm'] = data['stop'].apply(stemming)
x = data['stemm']
y = data['Duygu']

x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42)

# En çok kullanılan kelimeleri buluyor ve ağırlıklandırıyor. Böylece öznitelik çıkarımı yapılabiliyor.
vectorizer = TfidfVectorizer()

vectorizer.fit(x_train)
training_features = vectorizer.transform(x_train)
test_features = vectorizer.transform(x_test)
print(test_features)

# Destek Vektör Makineleri (Support Vector Machine) algoritmasının birçok hiper parametresi vardır.
# bunu araştırmacı manuel olarak belirlediği gibi parametreleri liste halinde sunarak ''GridSearchCV" arama ızgarasında
# eğitim verisi doğruluk skoruna göre tespit edebilir.
parametreler = {'C': [1, 10, 100, 1000], 'kernel': ['linear', 'rbf'],
                'gamma': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
                }
# hiper parametrelerin  doğruluk skorlarını oluştur
acc_scorer = make_scorer(accuracy_score)
# her parametrenin doğrulluk skorunu tek tek hesaplayan "GridSearchCV" ızgarasını oluştur.
# bunun için egitim verisine 10 kez çapraz geçerlilik sınaması yap
grid_obj = GridSearchCV(SVC(), parametreler, cv=10, scoring=acc_scorer)
grid_obj = grid_obj.fit(training_features, y_train)
# bulunan en iyi parametre kümesini modele ata ve modeli oluştur.
model = grid_obj.best_estimator_
accuracy = grid_obj.best_score_    # En iyi modelin doğruluğu hesaplanır.

# aşağıda, oluşturduğumuz modelin hiper parametreleri gösterilmektedir
model.fit(training_features, y_train)
y_pred = model.predict(test_features)
# print(y_pred)
print("Accuracy_score on the dataset:{:.2f}".format(
    accuracy_score(y_test, y_pred)))

# sns.set()
# mat = confusion_matrix(y_test, y_pred)
# sns.heatmap(mat.T, square=True, annot=True, fmt='d', cbar=False)
# plt.xlabel('true label')
# plt.ylabel('predicted label')
# plt.show()
