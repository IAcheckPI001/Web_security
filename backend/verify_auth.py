
import re
import os
import html
import random
from flask import Flask
import string
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from captcha.image import ImageCaptcha


app = Flask(__name__,template_folder="../frontend/templates",static_folder="../frontend/assets")

folder_path = f'{app.static_folder}/img/captcha_ss/'

def random_number():
    return random.randint(100, 999)

def generate_verification_code():
    code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
    return code

def generate_captcha():
    global folder_path
    captcha = ImageCaptcha()

    captcha_text = generate_verification_code()

    captcha_image_file = os.path.join(folder_path, f'{captcha_text}.png')
    captcha.write(captcha_text, captcha_image_file)

    file_name = f'{captcha_text}.png'

    return captcha_text, file_name

def destroy_captcha():
    global folder_path
    png_files_exist = False

    for filename in os.listdir(folder_path):
        if filename.endswith('.png'):
            png_files_exist = True
            break
    if png_files_exist:
        for filename in os.listdir(folder_path):
            if filename.endswith('.png'):
                file_path = os.path.join(folder_path, filename)
                os.remove(file_path)

def isvalidEmail(email):
    pattern = "^\S+@\S+\.\S+$"
    email_form = html.escape(email)
    objs = re.search(pattern, email_form)
    try:
        if objs.string == email_form:
            return True
    except:
        return False

def check_strong(password, password_config):
    check = True
    if len(password) < 13:
        check = False
        return check
    elif password != password_config:
        check = False
        return check
    elif bool(re.search(r"[A-Z]", password)) == False:
        check = False
        return check
    elif bool(re.search(r"[a-z]", password)) == False:
        check = False
        return check
    elif bool(re.search(r"[0-9]", password)) == False:
        check = False
        return check
    elif bool(re.search(r"[@#]", password)) == False:
        check = False
        return check

    return check


def remove_special_chars(input_string):
    cleaned_string = re.sub(r'[\"\'=\\-<>()]', '', input_string)
    return cleaned_string

def check_special_chars(input_string):
    cleaned_string = re.sub(r'[\"\'=<>()]', '', input_string)
    if cleaned_string != input_string:
        return True
    return False
    

def email_notice(email, password, email_sent, code):

    subject = '[AIShop] Account authentication code'
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(email, password)
    
    body = f"""
    <html>
    <body>
        <h1>Hi there !</h1>
        <p>Your authentication code is: <b>{code}</b></p>
        <br>
        <br>
        <p>Thanks,</p>
        <p>The AIShop Team</p>
    </body>
    </html>
    """
    html_message = MIMEText(body, 'html')
    html_message['Subject'] = subject
    html_message['From'] = "aishopProject@gmail.com"
    html_message['To'] = email_sent

    session.sendmail(email, email_sent, html_message.as_string())

def email_error(email, password, email_sent, content):

    subject = '[AIShop] Account authentication code'
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(email, password)
    current_datetime = datetime.now()
    body = f"""
    <html>
    <body>
        <h1>Hi there !</h1>
        <p>An error occurred. Error: <b>{content}</b></p>
        <br>
        <br>
        <p>Time the error occurred: {current_datetime}</p>
        <p>The AIShop Team</p>
    </body>
    </html>
    """
    html_message = MIMEText(body, 'html')
    html_message['Subject'] = subject
    html_message['From'] = "aishopProject@gmail.com"
    html_message['To'] = email_sent

    session.sendmail(email, email_sent, html_message.as_string())
