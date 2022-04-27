import re

def chain(data, *funcs):
    out = data
    for f in funcs:
        out = f(out)
    return out

def make_day_filename(class_date):
    return '{month}-{day}.txt'.format(month=class_date.month, day=class_date.day)

def remove_qa_stubs(text):
    if re.match('[Ii]nstructor:', text):
        return re.sub('[Ii]nstructor', '', text)
    elif re.match('my answer:', text.lower()):
        return re.sub('[Mm]y [Aa]nswer', '', text)
    return text