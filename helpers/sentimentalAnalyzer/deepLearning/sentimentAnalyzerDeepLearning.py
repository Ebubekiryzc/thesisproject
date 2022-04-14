from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
import numpy as np
import pandas as pd
from os import getcwd
from os.path import exists, join
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Embedding, LSTM
from tensorflow.keras.optimizers import Adam
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from tensorflow.python.keras.models import load_model
import re
import nltk
import pickle


location = join(getcwd(), "helpers", "sentimentalAnalyzer",
                "deepLearning", "sentiment_model.h5")

if(not exists(str(location))):
    nltk.download('punkt')
    nltk.download('stopwords')

WPT = nltk.WordPunctTokenizer()
stop_word_list = stopwords.words('turkish')
dataset = pd.read_excel(
    f'{join(getcwd(),"helpers","sentimentalAnalyzer","deepLearning","sentimentAnalysis.xlsx")}', sheet_name='Sheet1')


def remove_punctuation(text):
    return re.sub('[,\.!?:()"]', '', text)


def lowercase_text(text):
    return text.lower()


def strip_text(text):
    return text.strip()


def tokenize(values):
    words = nltk.tokenize.word_tokenize(values)
    filtered_words = [word for word in words if word not in stop_word_list]
    not_stopword_doc = " ".join(filtered_words)
    return not_stopword_doc


def set_tokenizer(data):
    tokenizer = Tokenizer(num_words=10000)
    tokenizer.fit_on_texts(data)
    return tokenizer


def export_tokenizer(tokenizer):
    with open(join(getcwd(), 'helpers', 'sentimentalAnalyzer', 'deepLearning', 'envVars', 'tokenizer.pickle'), 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)


def convert_to_sequences(tokenizer, text):
    return tokenizer.texts_to_sequences(text)


def get_max_tokens(train_input_tokens, test_input_tokens):
    num_tokens = [len(tokens)
                  for tokens in train_input_tokens + test_input_tokens]
    num_tokens = np.array(num_tokens)
    max_tokens = np.mean(num_tokens) + 2 * np.std(num_tokens)
    return int(max_tokens)


def export_max_tokens(max_tokens):
    with open(join(getcwd(), 'helpers', 'sentimentalAnalyzer', 'deepLearning', 'envVars', 'max_tokens.pickle'), 'wb') as handle:
        pickle.dump(max_tokens, handle, protocol=pickle.HIGHEST_PROTOCOL)


def get_pad_sequence(inputs, max_token):
    return np.array(pad_sequences(inputs, maxlen=max_token))


def tokens_to_string(tokenizer, tokens):
    idx = tokenizer.word_index
    inverse_map = dict(zip(idx.values(), idx.keys()))
    words = [inverse_map[token] for token in tokens if token != 0]
    text = ' '.join(words)
    return text


def set_model(embedding_size, max_tokens):
    model = Sequential()
    model.add(Embedding(input_dim=10000,
                        output_dim=embedding_size, input_length=max_tokens, name='embedding_layer'))
    model.add(LSTM(units=16, return_sequences=True))
    model.add(LSTM(units=8, return_sequences=True))
    model.add(LSTM(units=4))
    model.add(Dense(1, activation='sigmoid'))
    adam = Adam(learning_rate=0.001)
    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])
    return model


def fit_model(model, train_inputs, train_targets, epochs):
    history = model.fit(train_inputs, train_targets, epochs=epochs,
                        batch_size=64, validation_split=0.25)
    return model, history


def save_model(model, location):
    model.save(location)


def preprocess_text(text):
    text = remove_punctuation(text)
    text = lowercase_text(text)
    text = strip_text(text)
    text = tokenize(text)
    return text


def adjust_text_for_model(text, tokenizer, max_tokens):
    if(type(text) is not list):
        text = [text]
    tokens = tokenizer.texts_to_sequences(text)
    tokens_pad = pad_sequences(tokens, maxlen=max_tokens)
    return tokens_pad


def predict(text_will_predict):
    file_exists = exists(location)
    if (not file_exists):
        print('yok')
        dataset['Text'] = dataset['Text'].apply(
            lambda x: remove_punctuation(x))
        dataset['Text'] = dataset['Text'].apply(lambda x: lowercase_text(x))
        dataset['Text'] = dataset['Text'].apply(lambda x: strip_text(x))
        dataset['Text'] = dataset['Text'].apply(lambda x: tokenize(x))

        inputs = dataset['Text'].values.tolist()
        targets = dataset['Sentiment'].values.tolist()

        tokenizer = set_tokenizer(inputs)
        # Saving tokenizer
        export_tokenizer(tokenizer)

        x_train, x_test, y_train, y_test = train_test_split(
            inputs, targets, test_size=0.2, random_state=42)

        train_input_tokens = convert_to_sequences(tokenizer, x_train)
        test_input_tokens = convert_to_sequences(tokenizer, x_test)

        max_tokens = get_max_tokens(train_input_tokens, test_input_tokens)
        # Saving max_tokens
        export_max_tokens(max_tokens)

        train_inputs_pad_sequence = get_pad_sequence(
            train_input_tokens, max_tokens)

        model = set_model(50, max_tokens)
        model, history = fit_model(model, np.array(
            train_inputs_pad_sequence), np.array(y_train), 100)

        save_model(model, location)

        # Processing
        text_will_predict = preprocess_text(text_will_predict)

        # Adjusting for model
        tokens_pad = adjust_text_for_model(
            text_will_predict, tokenizer, max_tokens)

        # Prediction
        prediction = (model.predict(tokens_pad) > 0.5).astype("int32")
        return prediction
    else:
        print('model bulunuyor.')
        with open(join(getcwd(), 'helpers', 'sentimentalAnalyzer', 'deepLearning', 'envVars', 'tokenizer.pickle'), 'rb') as handle:
            tokenizer = pickle.load(handle)
        with open(join(getcwd(), 'helpers', 'sentimentalAnalyzer', 'deepLearning', 'envVars', 'max_tokens.pickle'), 'rb') as handle:
            max_tokens = pickle.load(handle)

        model = load_model(location)

        # Processing
        text_will_predict = preprocess_text(text_will_predict)

        # Adjusting for model
        tokens_pad = adjust_text_for_model(
            text_will_predict, tokenizer, max_tokens)

        # Prediction
        prediction = (model.predict(tokens_pad) > 0.5).astype("int32")
        return prediction
