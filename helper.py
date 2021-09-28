import re, imaplib 

class SpamDetection:

    def __init__(self):
        self.nonos = ['http', '<', '{', '(', '\\', '[', ')', '[']

    def clean_text(self, text):
        # text = re.sub('\W+',' ',text).strip()
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

    def classify(self, body, sender, subject, print_body=False):
        cleaned_body = self.clean_text(body)
        if print_body : 
            print(f'Body: {cleaned_body}\n')
        # pass through model 
        return False 

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
    mark_unseen(imap, mail_uid)
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