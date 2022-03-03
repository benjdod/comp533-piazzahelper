import html
from lib2to3.pgen2.token import OP
import logging
import sys
import os
import signal
import yaml
from datetime import date
from enum import Enum
from turtle import st
from selenium import webdriver
from util.config import get_config_field
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from util.generate import write_day, generate_diary
from util.parse import parse_imported

# config fields (change these as you see fit, I'm just too lazy to parse them as cmdline args)

LOG_LEVEL = logging.INFO
HEADLESS = True
class Operation(Enum):
    NOOP = 0
    IMPORT = 1
    BACKUP = 2
    COMMIT = 3
    MAKE_TODAY = 4
    ALL = 5

argpairs = [
    ('maketoday', Operation.MAKE_TODAY),
    ('import', Operation.IMPORT),
    ('backup', Operation.BACKUP),
    ('commit', Operation.COMMIT),
    ('all', Operation.ALL),
]

logger = logging.getLogger('piazza-helper')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(console_handler)
logger.setLevel(LOG_LEVEL)

def prompt_username():
    print("username: ")
    return input()

def prompt_passwd():
    print("password: ", end='')
    return input()

def prompt_login():
    return (prompt_username(), prompt_passwd())

def prompt_diarylink():
    print("Please enter your Piazza diary page link: ")
    return input()

def prompt_yesno(message):
    print(message + ' (y/n)', end=': ')
    sel = input().lower()
    if sel == 'y' or sel == 'yes':
        return True
    return False

def init_driver(driverPath):
    service = Service(driverPath)
    service.enableVerboseLogging = False
    service.suppressInitialDiagnosticInformation = True
    service.hideCommandPromptWindow = True
    service.start()

    browser_options = Options()

    browser_args = [
        "--window-size=1920x1080",
        "--disable-crash-reporter",
        "--disable-extensions",
        "--disable-in-process-stack-traces",
        "--disable-logging",
        "--disable-dev-shm-usage",
        "--log-level=3",
        "--output=/dev/null"
    ]

    if HEADLESS:
        browser_args.append('--headless')
        browser_args.append('--append-gpu')

    for arg in browser_args:
        browser_options.add_argument(arg)

    return webdriver.Chrome(service=service, options=browser_options)

def store_backup(text):
    backupDir = get_config_field('backupDir') or './backup'
    if backupDir[-1] != '/':
        backupDir += '/'
    today = date.today()
    fname = 'backup-{year}-{month}-{day}'.format(year=today.year, month=today.month, day=today.day)
    backup_dir_items = os.listdir(backupDir)

    i = 0
    for dir_item in backup_dir_items:
        if dir_item.startswith(fname):
            i += 1
    
    if i > get_config_field('maxBackups'):
        os.remove(backupDir + backup_dir_items[0])
    
    fname += '-' + str(i) + '.txt'
    with open(backupDir + fname, "w") as backup_file:
        backup_file.write(str(text))
    return fname

def print_usage():
    print('COMP 533 Piazza Helper Usage:')
    print('-----------------')
    print('maketoday - create a new file for today\'s class if it doesn\'t exist')
    print('-----------------')
    print('backup - backs up the current contents of your diary to disk')
    print('import - imports the contents of your diary to individual class files on disk')
    print('commit - writes all class files to your diary')
    print('all    - performs the above operations in sequence')

def parse_cmdline_args():
    argc = len(sys.argv)
    if argc < 2:
        print_usage()
        return Operation.NOOP

    for argp in argpairs:
        if sys.argv[1] == argp[0]:
            return argp[1]
    print_usage()
    return Operation.NOOP

    
username = get_config_field('username')
onyen = get_config_field('onyen')
diarylink = get_config_field('diaryLink')

# init driver

operation = parse_cmdline_args()

if operation == Operation.NOOP:
    sys.exit()

if operation == Operation.MAKE_TODAY:
    today = date.today()
    fname = get_config_field('classesDirectory')
    if fname[-1] != '/':
        fname += '/'
    classdate = '{month}-{day}'.format(month=str(today.month), day=str(today.day))
    fname += classdate + '.txt'
    if os.path.exists(fname):
        print('File for today\'s class exists at ' + fname)
    else:
        new_file = open(fname, 'a+')
        print('Created new file for today\'s class at ' + fname)
        
    sys.exit()

logger.info("initializing chrome web driver")
driver = init_driver(get_config_field('driverPath'))

def driver_close():
    global driver
    driver.close()
    return

if driver == None:
    logger.error('could not initialize chrome driver')
    sys.exit()

for signum in [
    signal.SIGBREAK,
    signal.SIGINT,
    signal.SIGTERM
]:
    signal.signal(signum, driver_close)

# 1. login to piazza

piazza_home_url = "https://piazza.com"
logger.info("navigating to " + piazza_home_url)
driver.get(piazza_home_url)
driver.maximize_window()

def try_login():
    global logger
    logger.info('attempting login')
    if get_config_field('username') != None:
        username = get_config_field('username')
        password = prompt_passwd()
    else:
        (username, password) = prompt_login()

    driver.find_element(By.ID, "email_field").send_keys(username)
    driver.find_element(By.ID, "password_field").send_keys(password)
    driver.find_element(By.ID, "modal_login_button").click()

try:
    driver.find_element(By.ID, "login_button").click()
    try:
        login_modal = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginModal"))
        )
    except:
        driver.quit()

    try_login()

    try:
        login_modal = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "userButton"))   # we can use this link to detect logged in
        )
    except:
        logger.error("failed to log in successfully")
        driver.quit()
except NoSuchElementException:
    pass

logger.info('successfully logged into Piazza')

# 2. get current diary text

if diarylink == None:
    diarylink = prompt_diarylink()

logger.info('navigating to diary post')
driver.get(diarylink)

def open_edit_mode():
    global driver
    global logger
    driver.find_element(By.XPATH, "//*[@id='view_question_note_bar']//*[@data-pats='edit_button']").click()

    # open edit mode
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "edit_question_note"))
        )
    except:
        logger.error("failed to open edit dialog")
        sys.exit()

logger.info('entering edit mode for diary post')
open_edit_mode()

driver.find_element(By.XPATH, "//input[@name='main_def_editor_question_note_edit' and @data-pats='details_plain_text_editor']").click()

logger.info('storing diary backup')
driver_textarea = driver.find_element(By.XPATH, "//*[@id='editor_question_note_edit']//*[@data-pats='editor_textarea']")
startingText = html.unescape(driver_textarea.get_attribute('value'))
backup_path = store_backup(startingText)
logger.info('stored diary backup as {fname}'.format(fname=backup_path))

if operation == Operation.BACKUP:
    driver.find_element(By.XPATH, "//a[@data-pats='cancel_button']").click()
    driver_close()
    logger.info('complete')

if operation == Operation.IMPORT or operation == Operation.ALL:
    classes = parse_imported(startingText)
    logger.info('writing class files')
    formed_classes = {}

    def tup_to_qa(tuple):
        return {'q': tuple[0], 'a': tuple[1]}

    for c in classes:
        formed_classes[c['date']] = list(map(tup_to_qa, c['qa']))
        write_day(c['date'], c['qa'])

    logger.info('wrote all class files. Please check them to ensure they were parsed correctly and fix any errors')

elif operation == Operation.COMMIT or operation == Operation.ALL:
    logger.info('generating diary text')
    diary_text = generate_diary()
    driver_textarea.clear()
    logger.info('writing diary to Piazza')
    for line in diary_text.splitlines():
        driver_textarea.send_keys(line)
        driver_textarea.send_keys(Keys.ENTER)
        driver_textarea.send_keys(Keys.ENTER)
    driver.find_element(By.XPATH, "//a[@data-pats='submit_button']").click()
    print('diary written - visit ' + get_config_field('diaryLink') + ' to ensure it was written correctly')

    logger.info("complete")
    driver_close()