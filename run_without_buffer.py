import imaplib, email, logging, time, os
import numpy as np 
from datetime import datetime
from helper import SpamDetection, sort_email, login, mark_unseen, update_buffer
from tqdm import tqdm

imap = login()
detect = SpamDetection()
spam_folder_name = "\"" + "Collegeboard spam" + "\""
buffer_file_path = 'buffer.npy'
current_path = os.getcwd()

DELAY_IN_SECONDS = 600

logging.basicConfig(filename="email.log", format='%(asctime)s %(message)s', filemode='w', force=True) 
logger = logging.getLogger()
logger.setLevel(logging.DEBUG) 

while True : 
    imap.select("inbox", readonly=False)
    _, mails = imap.search(None, 'UNSEEN')
    mails = mails[0].split()

    if len(mails) == 0 : 
        print('No unseen messages')
        logger.info('No unseen messages')
    else : 
        for uid in mails:
            _, data = imap.fetch(uid, '(RFC822)')
            _, b = data[0]
            email_msg = email.message_from_bytes(b)
            print('====================================')
            from_, subject = email_msg["from"], email_msg["subject"]
            print(f'uid: {uid} | from: {from_} | subject: {subject}')
            flag = False 
            for part in email_msg.walk():
                if part.get_content_type()=='text/plain' :
                    flag = True 
                    try : 
                        body = part.get_payload(decode=True).decode()
                        spam = detect.classify(body, from_, subject)
                        sort_email(imap, spam, uid, spam_folder_name)
                        logger.info(f"Spam: {spam} | From: {from_} | Subject: {subject}") 
                    except : 
                        logger.error('Could not decode email')

            if not flag : 
                logger.error('Email data not in plain text') 
            mark_unseen(imap, uid)

    print('--------- Waiting for next run ---------')
    for i in tqdm(range(10), leave=False, position=0):
        time.sleep(DELAY_IN_SECONDS/10)

