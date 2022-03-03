import re
import datetime
from util.config import get_config_field
from util.generate import write_day
from util.snippets import remove_qa_stubs


def parse_month_day_date(datestr):
    slash = datestr.index('/')
    month = int(datestr[:slash])
    day = int(datestr[slash+1:])
    this_date = datetime.datetime(2022, month, day)
    return this_date

def parse_imported(text):

    classes = []

    questions = []
    answers = []
    date = None

    for line in text.splitlines() + ['12/31:']:   # sentinel to make our lives easier :)
        line = line.strip()
        if line == '':
            continue

        # ignore spurious markdown tags (<md> particularly)
        if re.match(r'</?md>', line.lower()):
            continue

        # ignore pledge
        if re.match(r'i pledge that i attended', line.lower()):
            continue

        # ignore <onyen>, <name>, Diary line
        if re.match(r'{onyen},\s*.*,\s*Diary', line):
            continue

        if re.match(r'My Q&A:', line):
            continue

        if re.match(r'\d*/\d*', line):

            if date != None:
                if len(answers) != len(questions):
                    print('improper number of questions and answers for ' + date.isoformat())
                classes.append({'date': date, 'qa': list(zip(questions, answers))})

            if line[-1] == ':':
                line = line[:-1]
            print('setting new date: ', line)
            date = parse_month_day_date(line)
            questions = []
            answers = []

        elif re.match('instructor:', line.lower()):
            questions.append(re.sub('[Ii]nstructor:', '', line).strip())
        elif re.match('my answer:', line.lower()):
            answers.append(re.sub('[Mm]y [Aa]nswer:', '', line).strip())
        
    return classes
