import os
import re
import datetime
from util.config import get_config_field
from util.snippets import remove_qa_stubs, make_day_filename, chain

HONOR_PLEDGE = 'I pledge that I attended classes on the days reported below, the answers attributed to me in my Q&A were ones I articulated in class.'
NEWLINE = '\n'

def write_day(date, qa_tuples):
    filename = make_day_filename(date)
    print(filename)
    with open('./classes/{fname}'.format(fname=filename), 'w') as file:
        for pair in qa_tuples:
            file.write(pair[0])
            file.write("\n\n")
            file.write(pair[1])
            file.write("\n\n")

def write_days(days):
    for day in days:
        write_day(day[0], day[1])

"""
def double_up(list, acc=[]):
if len(list) > 0:
    if len(acc) == 0 or len(acc[-1]) == 2:
        acc.append(tuple([list[0]]))
    else:
        acc[-1] = tuple([acc[-1][0], list[0]])
    return double_up(list[1:], acc)
else:
    return acc
"""



def strip_lines(lines):
    return list(filter(lambda line: len(line) > 0, map(lambda line: line.strip(), lines)))

def double_up(l):
    return [e for e in zip(l[::2], l[1::2])]

def drop_no_answer(l):
    return list(filter(lambda qa: qa[1] != '-', l))

def generate_diary_tuples(classes_dir):
    class_files = os.listdir(classes_dir)
    class_files.sort(key=lambda s: list(map(int, re.sub(r'\.txt$', '', s).split('-'))))

    out = []

    for item in class_files:
        fullpath = os.path.join(os.path.abspath(classes_dir), item)
        if not os.path.isfile(fullpath):
            continue
        datestr = re.sub(r'\.txt$', '', item)
        datestr = re.sub(r'-', '/', datestr)

        data_obj = {}
        data_obj['date'] = datestr

        with open(fullpath) as classfile:
            data_obj['qa'] = chain(classfile, strip_lines, double_up, drop_no_answer)

        out.append(data_obj)

    return out

def generate_diary(classes_dir):
    
    out = ''

    out += HONOR_PLEDGE + NEWLINE
    out += '{onyen}, {name}, Diary'.format(onyen=get_config_field('onyen'), name=get_config_field('name'))
    out += NEWLINE

    qa_data = generate_diary_tuples(classes_dir)

    for class_data in qa_data:
        out += class_data['date'] + ':' + NEWLINE
        out += 'My Q&A:' + NEWLINE
        for qa in class_data['qa']:
            out += 'Instructor: ' + qa[0] + NEWLINE + 'My Answer: ' + qa[1] + NEWLINE
    
    return out