import imaplib 
import email
from helper import email_cleaner
import random

host = 'imap.gmail.com'

with open('/users/gursi/desktop/gmail_login.txt', 'r') as f : 
    username = f.readline().replace('\n','')
    password = f.readline().replace('\n','')

mail = imaplib.IMAP4_SSL(host)
mail.login(username, password)
mail.select('inbox', readonly=True)
print('Logged in.')

_, search_data = mail.search(None, 'UNSEEN')
mails = search_data[0].split()
random.shuffle(mails)

for num in mails:
    _, data = mail.fetch(num, '(RFC822)')
    _, b = data[0]
    email_msg = email.message_from_bytes(b)
    for header in ['subject', 'to', 'from', 'date']:
        print(f'{header}: {email_msg[header]}')
    for part in email_msg.walk():
        if part.get_content_type()=='text/plain' :
            body = part.get_payload(decode=True).decode()
            body = email_cleaner(body)
            print(body)
            with open('/users/gursi/desktop/email.txt', 'w') as f:
                f.writelines([body])
    break
