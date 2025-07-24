


from flask_login import login_user, current_user
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint, session, request, render_template, redirect, url_for

from .encypt import *
from .views import *
from .verify_auth import *
from back_end import set_permission
from .models import User, Status, Profile, Session, db


auth = Blueprint('auth', __name__)

ss_user = {}
email_verify = {}

email_ssmtp = "email@example.com"
password_ssmtp = "app_password" # Generate an app password for your email account

check = False
check_session = False
token_auth = ''
max_failed_attempts = 3
dialog = {'error': False, 'error_captcha': False, 'error_session': False, 'signUp': False ,'getPass': False}

captcha, img_captcha = generate_captcha()

@auth.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    global token_auth, check_session, ss_user, check, dialog, captcha, img_captcha
    if 'reload' not in session:
        dialog['getPass'] = False
        dialog['signUp'] = False
    session.pop('reload', None)
    token_auth = ''

    if current_user is not None:   
        if current_user.is_authenticated:
            return redirect(url_for('views.not_found'))
    dialog['error_captcha'] = False
    if request.method == 'POST':

        if 'pass--forget' in request.form:
            return redirect(url_for("auth.get_pass"))
        elif 'click--login' in request.form:
            ss_user = {}
            captcha_verify = request.form.get('captcha')
            if captcha != captcha_verify:
                destroy_captcha()
                captcha, img_captcha = generate_captcha()
                dialog['error_captcha'] = True
                return render_template("sign-in.html", dialog = dialog, captcha = captcha, img_captcha = img_captcha) 
            dialog['error_captcha'] = False
            email_form = request.form.get('username')
            passwd_form = request.form.get('password')

            if isvalidEmail(email_form):

                email_sha = create_sha256_hash(email_form)
                passwd_sha = create_sha256_hash(passwd_form)
                # query = text("EXEC sp_login :user, :password") # Used for MSSQL
                query = text("SELECT sp_login (:user, :password)")
                result = db.session.execute(query, {'user': email_sha, 'password': passwd_sha})
                check = False
                first_row = result.fetchone()
                db.session.commit()
                if isinstance(first_row[0], int) or first_row[0].isdigit():
                    dialog['error'] = True
                    if first_row[0] == -1:
                        destroy_captcha()
                        captcha, img_captcha = generate_captcha()
                        return render_template("sign-in.html", dialog = dialog, captcha = captcha, img_captcha = img_captcha)
                    else:
                        user_qr = User.query.filter_by(email = email_sha).first()
                        user_qr.login_failed = user_qr.login_failed + 1
                        db.session.commit()
                        if user_qr.login_failed >= max_failed_attempts:
                            token_auth = generate_csrf_token()
                            check = True
                            verification_code = generate_verification_code()
                            # verification_code = "abc123"
                            email_verify[token_auth] = {'code': verification_code, 'email_sha': email_sha, 'email' : user_qr.email, 'expires_in': 300, 'getPassAgain' : 0}
                            email_notice(email_ssmtp, password_ssmtp, email_form, verification_code)
                            return redirect(url_for('auth.sign_up_verify')) 
                        destroy_captcha()
                        captcha, img_captcha = generate_captcha()
                        return render_template("sign-in.html", dialog = dialog, captcha = captcha, img_captcha = img_captcha)                   
                else:
                    dialog['error'] = False
                    result_view = first_row[0]      
                    db.session.commit() 
                     
                    user_qr = User.query.filter_by(email = email_sha).first()
                    user_ss = Session.query.filter_by(email_user = email_sha).first()
                    if user_qr is None or user_ss is None:
                        dialog['error'] = True
                        destroy_captcha()
                        captcha, img_captcha = generate_captcha()
                        return render_template("sign-in.html", dialog = dialog, captcha = captcha, img_captcha = img_captcha)
                    if user_ss.ss_token == None:      

                        if result_view == "views.dashboards":
                            token = generate_csrf_token() +'2'
                        else:
                            token = generate_csrf_token() +'1'

                        current_datetime = datetime.now()

                        user_ss.ss_token = token
                        user_ss.date_login_rec = current_datetime
                        db.session.commit()
                        login_user(user_qr)
                        session[email_sha] = {'email': email_form, 'token': token, 'check_session': check_session}
                        
                        return redirect(url_for(result_view))
                    else:
                        ss_user = {'email_ss': email_sha, 'email_form': email_form, 'pass_ss': passwd_sha}
                        check_session = True
                        return redirect(url_for('auth.sign_in_ss'))
            else:
                destroy_captcha()
                captcha, img_captcha = generate_captcha()
                dialog['error'] = True
                return render_template("sign-in.html", dialog = dialog, captcha = captcha, img_captcha = img_captcha)
        elif 'check_ss' in request.form:
            if ss_user:
                dialog['error'] = False
                check_session = False
                # query = text("EXEC sp_login :user, :password") # Used for MSSQL
                query = text("SELECT sp_login (:user, :password)")
                result = db.session.execute(query, {'user': ss_user['email_ss'], 'password': ss_user['pass_ss']})
                first_row = result.fetchone()
                result_view = first_row[0]      
                db.session.commit() 
                user_qr = User.query.filter_by(email = ss_user['email_ss']).first()
                if result_view == "views.dashboard":
                    key = 'fskakmfka naskdn'
                    admin_uri = 'postgresql://syscus02:cus123#@localhost:5432/AIShop'
                    set_permission(key, admin_uri)
 
                login_user(user_qr)
                token = generate_csrf_token()
                session[ss_user['email_ss']] = {'email': ss_user['email_form'], 'token': token, 'check_session': check_session}
                current_datetime = datetime.now()
                user_ss = Session.query.filter_by(email_user = ss_user['email_ss']).first()
                user_ss.ss_token = token
                user_ss.date_login_rec = current_datetime
                db.session.commit()
                 
                return redirect(url_for(result_view)) 
    destroy_captcha()
    captcha, img_captcha = generate_captcha()  
    return render_template("sign-in.html", dialog = dialog, check_session = check_session, captcha = captcha, img_captcha = img_captcha) 

@auth.route('/sign-in-verify', methods=['GET', 'POST'])
def sign_in_ss():
    global ss_user, check_session, dialog, captcha, img_captcha

    check_session = True

    if current_user is not None:   
        if current_user.is_authenticated:
            return redirect(url_for('views.not_found'))
    if request.method == 'POST':
        check_session = False
        if ss_user:
            query = text("SELECT sp_login (:user, :password)")
            result = db.session.execute(query, {'user': ss_user['email_ss'], 'password': ss_user['pass_ss']})
            first_row = result.fetchone()
            result_view = first_row[0]      
            db.session.commit() 
            user_qr = User.query.filter_by(email = ss_user['email_ss']).first()
            if result_view == "views.dashboard":
                key = 'fskakmfka naskdn'
                admin_uri = 'postgresql://syscus02:cus123#@localhost:5432/AIShop'
                set_permission(key, admin_uri)

            login_user(user_qr)
            token = generate_csrf_token()
            session[ss_user['email_ss']] = {'email': ss_user['email_form'], 'token': token, 'check_session': check_session}
            current_datetime = datetime.now()
            user_ss = Session.query.filter_by(email_user = ss_user['email_ss']).first()
            user_ss.ss_token = token
            user_ss.date_login_rec = current_datetime
            db.session.commit()
                
            return redirect(url_for(result_view))
        else:
            destroy_captcha()
            captcha, img_captcha = generate_captcha() 
            dialog = {'error': False, 'error_captcha': False, 'error_session': True}    
            return redirect(url_for("auth.sign_in"))
     
    return render_template("sign-in.html", error = False, error_captcha = False, check_session = check_session, captcha = captcha, img_captcha = img_captcha)

@auth.route('/get-pass/', methods=['GET', 'POST'])
def get_pass():
    
    global token_auth
    token_auth = generate_csrf_token()

    if current_user is not None:   
        if current_user.is_authenticated:
            return redirect(url_for('views.not_found'))
        
    if request.method == 'POST':
        email_form = request.form.get('email_user')
        if isvalidEmail(email_form):
            email_sha = create_sha256_hash(email_form)

            user = db.session.query(User.email).filter(User.email == email_sha).first()
            if user is not None:
                verification_code = generate_verification_code()
                email_verify[token_auth] = {'code': verification_code, 'email_sha': email_sha, 'email' : email_form, 'expires_in': 300, 'getPassAgain' : 1}
                email_notice(email_ssmtp, password_ssmtp, email_form, verification_code)
                return redirect(url_for('auth.sign_up_verify')) 
            else:
                return render_template("getPass.html", error1 = True)
        else:
            return render_template("getPass.html", error = True)
    return render_template("getPass.html")

@auth.route('/sign-up/', methods=['GET', 'POST'])
def sign_up():
    global token_auth
    token_auth = generate_csrf_token()

    if current_user is not None:   
        if current_user.is_authenticated:
            return redirect(url_for('views.not_found'))
        
    if request.method == 'POST':
        email_form = request.form.get('email_user')
        
        if isvalidEmail(email_form):

            email_sha = create_sha256_hash(email_form)
            user = db.session.query(User.email).filter(User.email == email_sha).first()
            if user is None:
                verification_code = generate_verification_code()
                # verification_code = "abc123"
                email_verify[token_auth] = {'code': verification_code, 'email_sha': email_sha, 'email' : email_form, 'expires_in': 300, 'getPassAgain' : 0}
                email_notice(email_ssmtp, password_ssmtp, email_form, verification_code)
                return redirect(url_for('auth.sign_up_verify')) 
            else:
                return render_template("sign-up.html", error = True)
        else:
            return render_template("sign-up.html", error1 = True)
            
    return render_template("sign-up.html")
        

@auth.route('/sign-up--verify/', methods=['GET', 'POST'])
def sign_up_verify():
    
    global token_auth, check
    if token_auth not in email_verify and current_user.is_authenticated:
        return redirect(url_for('views.not_found'))
        
    if request.method == 'POST':
        if 'code--give_again' in request.form:
            if token_auth != '':
                # verification_code = "abc123"
                verification_code = generate_verification_code()
                email_verify[token_auth]['code'] = verification_code
                email_notice(email_ssmtp, password_ssmtp, email_verify[token_auth]['email'], verification_code)
                return render_template('sign-up--verify.html', checkGive = True)
            else:
                return redirect(url_for('views.not_found'))
        elif 'click--sigup' in request.form:
            code = request.form['code--verify']
            if token_auth in email_verify and email_verify[token_auth]['code'] == code :
                if check == False:
                    return redirect(url_for('auth.sign_up_passwd'))
                else:
                    try:
                        user_qr = User.query.filter_by(email = email_verify[token_auth]['email_sha']).first()
                        user_qr.login_failed = 0
                        db.session.commit()
                        dialog['error'] = False

                        return redirect(url_for('auth.sign_in'))
                    except:
                        return redirect(url_for('views.not_found'))
            else:
                return render_template('sign-up--verify.html', error = True)
        
    return render_template('sign-up--verify.html')


@auth.route('/sign-up--passwd/', methods=['GET', 'POST'])
def sign_up_passwd():
    global token_auth, dialog, email_verify

    if token_auth == '' or token_auth not in email_verify or current_user.is_authenticated:
        return redirect(url_for('views.not_found'))

    email_form = email_verify[token_auth]['email']
    check_step = email_verify[token_auth]['getPassAgain']
    email_sha = email_verify[token_auth]['email_sha']


    if request.method == 'POST':
        passwd = request.form['password']
        passwd_config = request.form['re--enter_password']

        if check_strong(passwd, passwd_config) == True:
            passwd_sha = create_sha256_hash(passwd_config)
            
            num_random = random_number()

            # get dữ liệu email
            parts = email_form.split('@')
            check_step = check_step

            # tạo khóa key phân biệt
            key_status = f'{parts[0][::2]}_sta{num_random}'
            key_session = f'{parts[0][::2]}_id{num_random}'
            key_profile = f'{parts[0][::2]}_pro{num_random}'

            # hàm lấy thời gian thực
            current_datetime = datetime.now()

            if check_step == 0:
                try:
                    new_status = Status(id_login=key_status, date_user_cre = current_datetime, date_pass_res = None)
                    db.session.add(new_status)
                    db.session.commit()

                    new_user = User(email=email_sha,passwd=passwd_sha,user_access="syscus02", user_status=key_status, login_failed = 0)
                    db.session.add(new_user)
                    db.session.commit()
                    
                    new_session = Session(id_user=key_session,email_user=email_sha, date_login_rec= current_datetime, ss_token = None)
                    db.session.add(new_session)
                    db.session.commit()

                    new_profile = Profile(id_profile=key_profile,name_user="New Name",avatar="/assets/img/160x160/account__logo-default.png", phone_number=None, address=None, access_user=key_session)
                    db.session.add(new_profile)
                    db.session.commit()
                    dialog['signUp'] = True
                    session['reload'] = 1
                    return redirect(url_for('auth.sign_in')) 
                except SQLAlchemyError as e:
                    error_message = str(e)
                    email_error(email_ssmtp, password_ssmtp, email_verify[token_auth]['email'], error_message)
                    db.session.rollback()
                    return redirect(url_for('views.not_found'))
                
            elif check_step == 1:
                current_datetime = datetime.now()
                # query = text("EXEC SP_GETPASS :user, :password, :date_update") # Used for MSSQL
                query = text("SELECT SP_GETPASS (:user, :password, :date_update)")
                result = db.session.execute(query, {'user': email_sha, 'password': passwd_sha, 'date_update': current_datetime})
                if result.returns_rows:
                    first_row = result.fetchone()
                    if isinstance(first_row[0], int) or first_row[0].isdigit():
                        if first_row[0] == -1:
                            return render_template('sign-up--passwd.html', check_error1 = True)
                
                db.session.commit()
                dialog['getPass'] = True
                session['reload'] = 1
                return redirect(url_for('auth.sign_in'))
                
        else:
            return render_template('sign-up--passwd.html', check_error = True)
    dialog['error'] = False
    dialog['error_captcha'] = False
    return render_template('sign-up--passwd.html')

