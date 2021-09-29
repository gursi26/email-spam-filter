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
            check_email = True
            buffer_exists = True
            if os.path.isfile(os.path.join(current_path, buffer_file_path)):
                buffer = np.load(os.path.join(current_path, buffer_file_path))
                if uid in buffer : 
                    check_email = False 
                    print(f'{uid} checked in last iteration')
            else : 
                buffer_exists = False 
                buffer = np.array([])
            
            if check_email : 
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
                if not spam : 
                    update_buffer(uid, buffer, buffer_file_path)
            mark_unseen(imap, uid)


        if buffer_exists : 
            stat = os.stat(os.path.join(current_path, buffer_file_path))
            buffer_creation_time = datetime.fromtimestamp(stat.st_birthtime)
            ctime = datetime.now()
            delta_time = (ctime - buffer_creation_time)
            hours = delta_time.total_seconds()/(60*60)
            if hours > 24 : 
                os.remove(os.path.join(current_path, buffer_file_path))
                logger.info(f"Buffer refreshed") 

    print('--------- Waiting for next run ---------')
    for i in tqdm(range(10), leave=False, position=0):
        time.sleep(DELAY_IN_SECONDS/10)

