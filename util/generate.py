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

def write_today():
    classes_dir = get_config_field('classesDirectory')
    daily_file = get_config_field('dailyFile')    

    with open(daily_file, 'r') as file:
        linetype = 'q'
        day_filename = make_day_filename(datetime.date.today())
        with open('{classes_dir}/{fname}'.format(classes_dir=classes_dir, fname=day_filename), 'w') as destfile:
            for line in file:
                line = line.strip()
                if line == '':
                    continue
                line = remove_qa_stubs(line)

                if linetype == 'q':
                    destfile.write(line + '\n')
                    linetype = 'a'
                else:
                    destfile.write(line + '\n\n')
                    linetype = 'q'

def generate_diary():
    
    out = ''

    out += HONOR_PLEDGE + NEWLINE
    out += '{onyen}, {name}, Diary'.format(onyen=get_config_field('onyen'), name=get_config_field('name'))
    out += NEWLINE

    for item in os.listdir('classes'):
        fullpath = os.path.join(os.path.abspath('classes'), item)
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

