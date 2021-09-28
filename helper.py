import imaplib, email
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
import pickle 
import torchtext
import numpy as np 
import pandas as pd 
import os

def construct_dataset():
    imap = login()
    detect = SpamDetection(model_path=None)
    spam_folder_name = "\"" + "Collegeboard spam" + "\""
    regular_folder_name = "\"" + "Not spam" + "\""

    tk = torchtext.data.get_tokenizer('basic_english')
    df_data = {'Text':[], 'Labels':[]}

    imap.select(spam_folder_name, readonly=False)

    _, mails = imap.search(None, 'SEEN')
    mails = mails[0].split()

    for i,uid in enumerate(mails):
        _, data = imap.fetch(uid, '(RFC822)')
        _, b = data[0]
        email_msg = email.message_from_bytes(b)
        print(f'Spam email {i+1} | From : {email_msg["from"]} | Subject : {email_msg["subject"]} |')
        for part in email_msg.walk():
            if part.get_content_type()=='text/plain' :
                try : 
                    body = part.get_payload(decode=True).decode()
                    cleaned_msg = detect.clean_text(body)
                    from_ = ' '.join([i for i in email_msg['from'].split(' ') if '<' not in i])
                    subject = email_msg['subject']
                    full_email = from_ + ' ' + subject + ' ' + cleaned_msg
                    full_email = ' '.join(tk(full_email))
                    df_data['Text'].append(full_email), df_data['Labels'].append(1)
                except : 
                    print('message could not be decoded')

    imap.select(regular_folder_name, readonly=False)

    _, mails = imap.search(None, 'SEEN')
    mails = mails[0].split()

    for i,uid in enumerate(mails):
        _, data = imap.fetch(uid, '(RFC822)')
        _, b = data[0]
        email_msg = email.message_from_bytes(b)
        print(f'Non-spam email {i+1} | From : {email_msg["from"]} | Subject : {email_msg["subject"]} |')
        for part in email_msg.walk():
            if part.get_content_type()=='text/plain' :
                try : 
                    body = part.get_payload(decode=True).decode()
                    cleaned_msg = detect.clean_text(body)
                    from_ = ' '.join([i for i in email_msg['from'].split(' ') if '<' not in i])
                    subject = email_msg['subject']
                    full_email = from_ + ' ' + subject + ' ' + cleaned_msg
                    full_email = ' '.join(tk(full_email))
                    df_data['Text'].append(full_email), df_data['Labels'].append(0)
                except : 
                    print('message could not be decoded')

    df = pd.DataFrame(df_data)
    df.to_csv('dataset.csv', index=False)


class SpamDetection:

    def __init__(self, model_path='model.pickle'):
        self.nonos = ['http', '<', '{', '(', '\\', '[', ')', '[']
        self.tk = torchtext.data.get_tokenizer('basic_english')
        if not model_path == None : 
            with open('model.pickle','rb') as f : 
                self.cv, self.tfidf, self.model = pickle.load(f)

    def clean_text(self, text):
        text = text.replace('\n', '')
        text = text.replace('\r', ' ')
        subs = text.split(' ')
        subs = list(filter(('').__ne__, subs))
        
        to_remove = []
        for token in subs : 
            flag = True 
            for nono in self.nonos : 
                if nono in token : 
                    flag = False 
                    break 
            if not flag : 
                to_remove.append(token)

        output = [i for i in subs if i not in to_remove]
        text = ' '.join(output)
        return text 

    def preprocess(self, body, sender, subject):
        output = sender + ' ' + subject + ' ' + body 
        output = ' '.join(self.tk(output))
        output = self.tfidf.transform(self.cv.transform(np.array([output])))
        return output
        

    def classify(self, body, sender, subject):
        cleaned_body = self.clean_text(body)
        model_input = self.preprocess(cleaned_body, sender, subject)
        pred = self.model.predict(model_input)[0]
        return bool(pred) 

def login(creds_path="/users/gursi/documents/gmail_login.txt"):
    host = 'imap.gmail.com'
    with open(creds_path, 'r') as f : 
        username = f.readline().replace('\n','')
        password = f.readline().replace('\n','')

    imap = imaplib.IMAP4_SSL(host)
    imap.login(username, password)
    print('Logged in.')
    return imap

def mark_unseen(imap, mail_uid):
    r = imap.store(mail_uid, '-FLAGS', '\Seen')
    if r[0] == 'OK':
        print('Mail marked as unseen.')

def relabel_and_delete(imap, mail_uid, spam_folder_name):
    r1 = imap.store(mail_uid, '+X-GM-LABELS', spam_folder_name)
    if r1[0] == 'OK':
        print('Mail relabeled.')
        r3 = imap.store(mail_uid, "+FLAGS", "\\Deleted")
        if r3[0] == 'OK' : 
            print('Mail deleted.')

def sort_email(imap, spam, mail_uid, spam_folder_name):
    if spam : 
        print('Spam detected.')
        relabel_and_delete(imap, mail_uid, spam_folder_name)
    else : 
        print('No spam detected.')
        mark_unseen(imap, mail_uid)

def update_buffer(uid, buffer, buffer_file_path, current_path=os.getcwd()):
    buffer = np.append(buffer, np.array([uid]))
    np.save(os.path.join(current_path, buffer_file_path[:-4]), buffer)

def test() :
    detect = SpamDetection()
    text = "Would you like to be part of a vibrant community of students? An enriching experience awaits you at Drexel University!"
    sender = "Drexel University"
    subject = "Apply now"
    print(detect.classify(text, sender, subject))

    text = "Your university applications are due. Please send them in through Google Classroom as soon as possible."
    sender = "NPS College counselling department"
    subject = "University applications"
    print(detect.classify(text, sender, subject))

#test()