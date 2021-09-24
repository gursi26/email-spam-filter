nonos = ['http', '<', '{']

def email_cleaner(text):
    subs = text.split(' ')
    for sub in subs:
        flag = True 
        for nono in nonos : 
            if sub.startswith(nono):
                flag = False 
                break 
        if not flag : 
            subs.remove(sub)
    text = ' '.join(subs)
    return text 

