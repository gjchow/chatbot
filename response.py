import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import load_model
import json
import random
import pickle
import numpy as np

lemmatizer = WordNetLemmatizer()

model = load_model('chatbot_model.h5')

ERROR_THRESHOLD = 0.1
# open things to be read
intents = json.loads(open('intents.json').read())
words_ = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))


# lemmatize and clean up the words in a sentence
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


# creates a bag of words for the cleaned up sentences
def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print('found in bag: %s' % w)
    return np.array(bag)


# shows the intents and the likelihood
def predict_class(sentence, model_):
    p = bow(sentence, words_, show_details=False)
    res = model_.predict(np.array([p]))[0]
    results = []
    for i, r in enumerate(res):
        print(classes[i], r)
        if r > 1-ERROR_THRESHOLD:
            results.append([i, r])
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    if len(results) == 0:
        return_list.append({'intent': 'unknown', 'probability': '1'})
    else:
        for r in results:
            return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    print(return_list)
    return return_list


# outputs the response from the intent with the highest probability
# change this to get different responses depending on tag
def get_response(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            return result


# takes in the message and outputs a response after predicting intent
def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = get_response(ints, intents)
    return res


print(chatbot_response("what is csc148"))