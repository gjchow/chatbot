import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import load_model
import json
import random
import pickle
import numpy as np
import information
import re
from typing import List

lemmatizer = WordNetLemmatizer()

model = load_model('training_info/chatbot_model.h5')

ERROR_THRESHOLD = 0.25
# open things to be read
intents = json.loads(open('intents.json').read())
words_ = pickle.load(open('training_info/words.pkl', 'rb'))
classes = pickle.load(open('training_info/classes.pkl', 'rb'))


# lemmatize and clean up the words in a sentence
def clean_up_sentence(sentence: str):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


# creates a bag of words for the cleaned up sentences
def bow(sentence: str, words: List[str], show_details=True):
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
def predict_class(sentence: str, model_: model, show_details=True):
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
def get_response(ints, intents_json, sentence: str) -> List[str]:
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
                    result = information.course_info(course)
                elif tag == 'prereq':
                    result = information.course_prereq(course)
                elif tag == 'breadth':
                    result = information.course_breadth(course)
                elif tag == 'description':
                    result = information.course_descrip(course)
                elif tag == 'exclusion':
                    result = information.course_exclu(course)
                elif tag == 'link':
                    result = information.course_link(course)
                elif tag == 'need':
                    code = get_code(sentence)
                    result = information.needed_in(course, code, False)
            return result


def get_course(sentence: str):
    words = list(sentence.split())
    utsg = re.compile(r'^\w{3}\d{3}$')
    utsc = re.compile(r'^\w{3}[A-Da-d]\d{2}$')
    for word in words:
        is_utsg = re.match(utsg, word)
        is_utsc = re.match(utsc, word)
        if is_utsg:
            return word
        if is_utsc:
            return word
    return ''


def get_code(sentence: str):
    words = list(sentence.split())
    code = re.compile(r'^\w{3}$')
    for word in words:
        is_code = re.match(code, word)
        if is_code:
            return word
    return ''

# takes in the message and outputs a response after predicting intent
def chatbot_response(msg):
    ints = predict_class(msg, model, show_details=False)
    res = get_response(ints, intents, msg)
    return res