import nltk
from nltk.stem import WordNetLemmatizer
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import SGD
import random
import json
import pickle
nltk.download('punkt')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

words = []
classes = []
documents = []
ignore_words = ['?', '!']

data_file = open('intents.json').read()
intents = json.loads(data_file)

for intent in intents['intents']:
    for pattern in intent['patterns']:
        # tokenizing each word
        w = nltk.word_tokenize(pattern)
        words.extend(w)
        # adding to documents
        documents.append((w, intent['tag']))
        # adding tag to classes if not already there
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

temp = []
for w in words:
    if w not in ignore_words:
        temp.append(lemmatizer.lemmatize(w.lower()))

words = temp
words = sorted(list(set(words)))

classes = sorted(list(set(classes)))

print(len(documents), "documents")
print(len(classes), "classes", classes)
print(len(words), "unique lemmatized words", words)

pickle.dump(words, open('training_info/words.pkl', 'wb'))
pickle.dump(classes, open('training_info/classes.pkl', 'wb'))

# initializing training
training = []
output_empty = [0]*len(classes)
for doc in documents:
    # bag of words
    bag = []
    pattern_words = doc[0]
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    for w in words:
        if w in pattern_words:
            bag.append(1)
        else:
            bag.append(0)

    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1

    training.append([bag, output_row])

random.shuffle(training)
training = np.array(training)
# create train and test lists where x is patterns and y is intents
train_x = list(training[:, 0])
train_y = list(training[:, 1])
print('Training data created')

# Model
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

hist = model.fit(np.array(train_x), np.array(train_y), epochs=2000, batch_size=5, verbose=1)
model.save('training_info/chatbot_model.h5', hist)

print("Model created")