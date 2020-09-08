import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import load_model
import json
import random
import pickle
import numpy as np
import scraper
import re

lemmatizer = WordNetLemmatizer()

model = load_model('chatbot_model.h5')

ERROR_THRESHOLD = 0.2
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
def predict_class(sentence, model_, show_details=True):
    p = bow(sentence, words_, show_details=False)
    res = model_.predict(np.array([p]))[0]
    results = []
    for i, r in enumerate(res):
        if show_details:
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
    return return_list


# outputs the response from the intent with the highest probability
# change this to get different responses depending on tag
def get_response(ints, intents_json, sentence):
    result = ''
    text_response = ['greeting', 'goodbye', 'help', 'thanks', 'unknown']
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            if tag in text_response:
                result = [random.choice(i['responses'])]
            else:
                course = get_course(sentence)
                if tag == 'search':
                    result = scraper.course_info(course)
                elif tag == 'prereq':
                    result = scraper.course_prereq(course)
                elif tag == 'breadth':
                    result = scraper.course_breadth(course)
                elif tag == 'description':
                    result = scraper.course_descrip(course)
                elif tag == 'exclusion':
                    result = scraper.course_exclu(course)
                elif tag == 'link':
                    result = scraper.course_link(course)
            return result


def get_course(sentence):
    words = list(sentence.split())
    is_utsg = False
    is_utsc = False
    utsg = re.compile(r'^\w{3}\d{3}$')
    utsc = re.compile(r'^\w{3}[A-Da-d]\d{2}$')
    for word in words:
        if not is_utsg and not is_utsc:
            is_utsg = re.match(utsg, word)
            if is_utsg:
                return word
            is_utsc = re.match(utsc, word)
            if is_utsc:
                return word
    return ''


# takes in the message and outputs a response after predicting intent
def chatbot_response(msg):
    ints = predict_class(msg, model, show_details=False)
    res = get_response(ints, intents, msg)
    return res

chatbot_response('what is mat137')