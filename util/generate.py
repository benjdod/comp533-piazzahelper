import os
import re
import datetime
from util.config import get_config_field
from util.snippets import remove_qa_stubs, make_day_filename

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

def generate_diary():
    
    out = ''

    out += HONOR_PLEDGE + NEWLINE
    out += '{onyen}, {name}, Diary'.format(onyen=get_config_field('onyen'), name=get_config_field('name'))
    out += NEWLINE

    class_files = os.listdir(get_config_field('classesDirectory'))
    class_files.sort(key=lambda s: list(map(int, re.sub(r'\.txt$', '', s).split('-'))))

    for item in class_files:
        fullpath = os.path.join(os.path.abspath(get_config_field('classesDirectory')), item)
        if not os.path.isfile(fullpath):
            continue
        datestr = re.sub(r'\.txt$', '', item)
        datestr = re.sub(r'-', '/', datestr)
        out += datestr + ':' + NEWLINE
        out += 'My Q&A:' + NEWLINE

        with open(fullpath) as classfile:
            side = 'q'
            for line in classfile:
                line = line.strip()

                if line == '':
                    continue 
                if side == 'q':
                    out += 'Instructor: ' + line
                    side = 'a'
                else:
                    out += 'My Answer: ' + line
                    side = 'q'
                out += NEWLINE

    return out

