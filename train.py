from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import numpy as np 
import pandas as pd 
import pickle
from helper import construct_dataset

construct_dataset(spam_name='Collegeboard spam', nonspam_name='Not spam')
df = pd.read_csv('dataset.csv')
df.head()

x_train, x_test, y_train, y_test = train_test_split(df['Text'], df['Labels'], test_size=0.2)
cv = CountVectorizer()
x_train_counts = cv.fit_transform(x_train)
tfidf = TfidfTransformer()
x_train_tfidf = tfidf.fit_transform(x_train_counts)

print('-----------------------------------------------------------')
print('Training model')
model = MultinomialNB().fit(x_train_tfidf, y_train)

x_test_counts = cv.transform(x_test)
x_test_tfidf = tfidf.transform(x_test_counts)
yhat = model.predict(x_test_tfidf)

acc = accuracy_score(y_test, yhat)
print(f'Accuracy : {acc}')

to_save = [cv, tfidf, model]
with open('model.pickle','wb') as f : 
    pickle.dump(to_save, f)
print('Model saved')
