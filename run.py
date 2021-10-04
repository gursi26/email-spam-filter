import imaplib, email, logging, time, os
import numpy as np 
from datetime import datetime
from helper import SpamDetection, sort_email, login, mark_unseen, update_buffer, read_by_bot
from tqdm import tqdm

imap = login()
detect = SpamDetection()
spam_folder_name = "\"" + "Collegeboard spam" + "\""
bot_read_label = "\"" + "Read by bot" + "\""
current_path = os.getcwd()

imap.select("inbox", readonly=False)
_, mails = imap.search(None, 'UNSEEN')
mails = mails[0].split()

if len(mails) == 0 : 
    print('No unseen messages')
else : 
    for uid in mails: 
        _, labels = imap.fetch(uid, '(X-GM-LABELS)')
        _, data = imap.fetch(uid, '(RFC822)')
        _, b = data[0]
        email_msg = email.message_from_bytes(b)
        print('====================================')
        from_, subject = email_msg["from"], email_msg["subject"]
        print(f'uid: {uid} | from: {from_} | subject: {subject}')
        if not 'Read by bot' in str(labels[0]):
            flag = False 
            for part in email_msg.walk():
                if part.get_content_type()=='text/plain' :
                    flag = True 
                    try : 
                        body = part.get_payload(decode=True).decode()
                    except : 
                        body = str(part)
                    spam = detect.classify(body, from_, subject)
                    sort_email(imap, spam, uid, spam_folder_name)

            if not flag : 
                print('Email data not in plain text') 
            read_by_bot(imap, uid, bot_read_label)
        else : 
            print('Mail already read by bot.')
        mark_unseen(imap, uid)
