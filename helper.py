import re 

nonos = ['http', '<', '{', '(', '\\', '[', ')', '[']

def email_cleaner(text):
    text = re.sub('\W+',' ',text).strip()
    text = text.replace('\n', '')
    text = text.replace('\r', '')
    subs = text.split(' ')
    subs = list(filter(('').__ne__, subs))
    
    to_remove = []
    for token in subs : 
        flag = True 
        for nono in nonos : 
            if nono in token : 
                flag = False 
                break 
        if not flag : 
            to_remove.append(token)

    output = [i for i in subs if i not in to_remove]
    text = ' '.join(output)
    return text 

