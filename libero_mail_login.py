#!/usr/bin/env python3

# per fare il login a un paio di account mail di libero.it
# che tengo di riserva ma che non uso praticamente mai...
# Per velocizzare le cose (visto che quel sito è pure una merda)
# quando libero.it dice di loggarsi altrimenti le disattiva.

import getpass
import time

# https://github.com/crap0101/py_warnings
from py_warnings import pywarn

try:
    import keyring
    KEYRING_OK = True
except ImportError:
    KEYRING_OK = False
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

CHROME_DRIVER = "/usr/bin/chromedriver"
DEFAULT_URL = "https://login.libero.it/?ref=hpl-hdx"

def get_driver (driver_path, headless=True):
    service = Service(executable_path=driver_path)
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    return webdriver.Chrome(service=service, options=options)

def login (username, pw, url, driver, default_driver_wait=2, sleeptime=0.5):
    try:
        driver.get(url)
        time.sleep(sleeptime)
        wait = WebDriverWait(driver, default_driver_wait)
        try:
            no_cookie = wait.until(EC.element_to_be_clickable((By.ID, "iol_cmp_cont_senz_acce")))
            no_cookie.click()
            print("refusing cookies...")
            really_no_cookie = "ubl__cnt__btn ubl-ncs__btn ubl-cst__btn ubl-ncs__btn--reject iubenda-cs-reject-btn"
            fuck_cookie = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, '.'.join(really_no_cookie.split()))))
            fuck_cookie.click()
            print("accepting required cookies...")
        except Exception as e:
            print(f"GNAM: '{e}'")
            print("No cookie banner?")

        username_field = wait.until(EC.presence_of_element_located((By.ID, "loginid")))
        username_field.clear()
        username_field.send_keys(username)
        usubmit = wait.until(EC.element_to_be_clickable((By.ID, "form_submit")))
        driver.execute_script("arguments[0].click();", usubmit)
        print("go to the pw page...")

        time.sleep(sleeptime)
        print("waiting...")
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
        time.sleep(sleeptime)
        print("forcing DOM...")
        driver.execute_script(f"arguments[0].value = '{pw}';", password_field)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", password_field)

        print("pw submit...")
        driver.execute_script("document.forms['autenticazione'].submit();")
        print("logged!")
        return True
    except Exception as e:
        print(f"BURP: '{e}'")
        return False
    finally:
        driver.quit()

def backend_names ():
    return list(b.name for b in keyring.get_keyring().backends)

def get_backend (name):
    k = keyring.get_keyring()
    for b in k.backends:
        if b.name == name:
            return b
    return None

def set_backend (name):
    if (b:= get_backend(name)) is not None:
        keyring.set_keyring(b)
    else:
        raise ValueError(f"No available backend named {name}")

def get_keyring_password (service, user):
    return keyring.get_password(service, user)

def get_credential ():
    user = input("user: ")
    pw = getpass.getpass()
    return user, pw


def get_parser ():
    descr = '''
Logs to the give urls and exit.
Meant to a very specifci task (logging to libero.it mail service,
doesn't have capability to log in other sites (for now).
So, the command line options are, at this time, not very useful,
but written for (possibly) future extensions.

The -s, -p and -u options (and the positional arguments URL)
accepts a variable number of argument which will be paired
to do the logging task; so the user must provide the same number
of arguments to each, unless the -S option is used, in which case
the same url (the first provided) will be used to logging with
each credential provided.

Alternatively, the -c option can be used multiple times, providing
a pair of username/password or username/service.

With the -s and -c options the -p and -P options will be ignored and a warning
will be printed.
Also, using the -c option cause ignoring the -s and -u options and
a warning will be printed.

EXAMPLES:
    %prog -p pw1 pw2 -u user1 user2 -- url1 url2
        Logs to url1 using pw1 and user1 credential
        and to url2 using pw2 and user2 credential.
    %prog -s s1 s2 -u user1 user2 -- url1 url2
        This, in a similar way, logs using the keyring module,
        logging to url1 using the service name s1 and user1 credential
        and to url2 using the service name s2 and user2 credential.
    %prog -c u1 s1 -c u2 s1
    '''
    parser = argparse.ArgumentParser(description=descr,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-b', '--backend',
                        dest='backend', choices=backend_names(),
                        help='available keyring backend (or let the keyring module choose one)')
    parser.add_argument('-c', '--credential',
                        dest='credential', nargs=2, default=[], action='append',
                        help='''credential pairs: interpreted as username/password by default,
                        as username/service if the -k option is given.''')
    parser.add_argument('-k', '--credential-as-keyring',
                        dest='k_credential', action='store_true',
                        help='''interprets the credential pairs given with the -c option
                        as username/service to be used with the keyring module''')
    parser.add_argument('-d', '--driver-wait-time',
                        dest='drive_wait', type=float, default=2,
                        help='selenium driver wait time, default: %(default)ss')
    parser.add_argument('-D', '--driver',
                        dest='driver', default=CHROME_DRIVER,
                        help='selenium driver path, default %(default)s')
    parser.add_argument('-H', '--headless',
                        action='store_true',
                        help='run the browser in headless mode.')
    parser.add_argument('-s', '--service',
                        dest='services', nargs='+',
                        help='keyring service(s)')
    p = parser.add_mutually_exclusive_group()
    p.add_argument('-P', '--ask-password',
                   dest='ask_pw', action='store_true',
                   help='prompt for password(s) for each listed user(s)')
    p.add_argument('-p', '--password',
                   dest='passwords', nargs='+', default=[],
                   help='password(s)')
    parser.add_argument('-S', '--single',
                        dest='single', action='store_true',
                        help='use the same url for every user/password (or service/user) pair')
    parser.add_argument('-t', '--sleep-time',
                        dest='sleep_time', default=0.5,
                        help='system sleep time, default: %(default)ss')
    parser.add_argument('-u', '--user',
                        dest='users', nargs='+', default=[],
                        help='user(s)')
    parser.add_argument('-w', '--warning-level',
                        dest='warn', choices=pywarn.WARN_OPT, default=pywarn.ALWAYS_WARNINGS,
                        help='warning level, default: %(default)s')
    parser.add_argument('urls',
                        nargs='*',
                        help=f'url(s). if no urls, uses {DEFAULT_URL}')
    return parser


if __name__ == '__main__':
    import argparse
    import sys
    parser = get_parser()
    args = parser.parse_args()

    # set warning level
    def warn (message):
        pywarn.warn(pywarn.CustomWarning(message))
    pywarn.set_filter(args.warn, pywarn.CustomWarning)
    pywarn.set_showwarning(pywarn.bare_showwarning)
    
    # check for conflicting options, missing modules or arguments, etc.:
    if not args.urls:
        args.urls = [DEFAULT_URL]
    if (args.services or args.backend) and not KEYRING_OK:
        parser.error("No keyring module found!")
    if args.backend and not (args.services or args.credential):
        warn("setting the backend (-b) but no services (-s) or credential (-c)")
    if args.services and (args.passwords or args.ask_pw):
        args.passwords = []
        args.ask_pw = None
        warn("using -s option, ignoring -p and -P options")
    if args.credential:
        if args.passwords or args.ask_pw:
            args.passwords = []
            args.ask_pw = None
        warn("using -c option, ignoring -p and -P options")
        if args.services:
            args.services = []
            warn("using -c option, ignoring -s option")
        if args.users:
            args.users = []
            warn("using -c option, ignoring -u option")
    # at least credential or users must present (not so optional :D)
    if (args.users and (len(args.urls) != len(args.users))
        or (args.credential and (len(args.urls) != len(args.credential)))):
        if not args.single:
            parser.error("discrepancy between the number of urls and the given credential")
        else:
            u = args.urls[0]
            args.urls = list(u for _ in (args.users or args.credential))

    # possibly backend choice:
    if args.backend:
        set_backend(args.backend)
        
    # use keyring?
    if args.credential:
        if args.k_credential:
            data = list((u, get_keyring_password(s, u), U) for (u, s), U in zip(args.credential, args.urls))
        else:
            data = list((*c, url) for c, url in zip(args.credential, args.urls))
    elif args.services:
        if len(args.users) != len(args.services):
            parser.error("discrepancy between the number of usernames and services")
        try:
            data = list([u, get_keyring_password(s, u), U] for u,s,U in zip(args.users, args.services, args.urls))
        except Exception as e:
            parser.error(f'{e}')
    else:
        if args.ask_pw:
            data = list([u, getpass.getpass(f"password for {u}:"), U] for u, U in zip(args.users, args.urls))
        else:
            if len(args.users) != len(args.passwords):
                parser.error("discrepancy between the number of usernames and passwords")
            data = list(zip(args.users, args.passwords, args.urls))
    #print(args); print(data)
    #exit()

    fail = 0
    for user, pw, url in data:
        print(f"*** Logging {user} to {url} ...")
        if not login(user, pw, url, get_driver(args.driver)):
            print("^^^ Error during login of", user)
            fail = 1

    sys.exit(fail)
