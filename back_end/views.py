
from flask import Blueprint, session, request, render_template, redirect, url_for
from flask_login import current_user, logout_user, login_required
from datetime import datetime, timedelta
import pandas as pd 

from .models import  Session, Profile, Product, Cart, CardPay, Order, StatusOrder, db
from .verify_auth import *


views = Blueprint('views', __name__)

check_view = False
order_list = []
pay_info = {}
pay_1_pro = {}
code_verify = {}

email_ssmtp = "email@example.com"
password_ssmtp = "app_password"

#--------------------- Customer - AIShop

@views.route('/not-found', methods=['GET', 'POST'])
def not_found():
    return render_template("NotFound.html")

@views.route('/sesion-expires', methods=['GET', 'POST'])
def sesion_expires():
    return render_template("session_expires.html")

@views.route('/',methods=['GET', 'POST'])
def home():
    global product_buy, order_list, pay_info, check_view, pay_1_pro
    product_buy = {}
    pay_info = {}
    pay_1_pro = {}
    order_list = []
    products = db.session.query(Product).all()
    if current_user is not None:   
        if current_user.is_authenticated:
            user_ss = Session.query.filter_by(email_user = current_user.email).first()
            if user_ss.ss_token != session[current_user.email]['token']:           
                return redirect(url_for("views.sign_out"))
            if session[current_user.email]['token'][-1] == '2':
                return redirect(url_for("views.dashboards"))
    return render_template("/index.html", user=current_user, check_view = check_view, product_list = products)

@views.route('/sign-out')
@login_required
def sign_out():
    global check_view
    check_view = False
    user_ss = Session.query.filter_by(email_user = current_user.email).first()
    if user_ss.ss_token == session[current_user.email]['token']:
        user_ss.ss_token = None
        db.session.commit()
    
    session.pop(current_user.email, None)
    logout_user()
    return redirect(url_for("auth.sign_in"))

@views.route('/shop', methods=['GET', 'POST'])
def shop():
    global check_view
    products = db.session.query(Product).all()
    if current_user is not None:   
        if current_user.is_authenticated:
            user_ss = Session.query.filter_by(email_user = current_user.email).first()
            if user_ss.ss_token != session[current_user.email]['token']:           
                return redirect(url_for("views.sign_out"))
    if request.method == 'POST':
        if 'view_product' in request.form:
            id_pro = request.form.get('id_product')
            return redirect(url_for('views.shop_single', id = id_pro))
        elif 'add_product' in request.form:
            id_pro = request.form.get('id_product')
            return redirect(url_for('views.shop_single', id = id_pro))
        elif 'like_product' in request.form:
            print("da like")
    
    return render_template("shop.html",user=current_user, check_view = check_view, product_list = products)

product_buy = {}
@views.route('/shop-single/<id>', methods=['GET', 'POST'])
def shop_single(id):
    try:
        global check_view, product_buy
        if current_user is not None:   
            if current_user.is_authenticated:
                user_ss = Session.query.filter_by(email_user = current_user.email).first()
                if user_ss.ss_token != session[current_user.email]['token']:           
                    return redirect(url_for("views.sign_out"))
        if id.isdigit():
            product_detail = Product.query.filter_by(id_product = int(id)).first()
            if product_detail is None:
                return redirect(url_for("views.not_found")) 
        else:
            return redirect(url_for("views.not_found")) 
        products = db.session.query(Product).all()
        product_detail = Product.query.filter_by(id_product = int(id)).first()
        check_auth = True
        if request.method == 'POST':
            if 'add--cart' in request.form:
                if current_user is not None:   
                    if current_user.is_authenticated:
                        if check_view == True:
                            return redirect(url_for('views.dashboards'))

                        quality = request.form.get('product-quanity')
                        current_datetime = datetime.now()

                        if user_ss:
                            user_profile = Profile.query.filter_by(access_user=user_ss.id_user).first()
                        else:
                            return redirect(url_for('auth.sign-in'))
                        formatted_time = current_datetime.strftime("%H%S%M%d")

                        id_cart = f'{user_profile.id_profile}_{id}_{formatted_time}'
                        pro_exit = Cart.query.filter_by(product_cart = int(id)).first()
                        
                        if not pro_exit or pro_exit.status_cart == 2:
                            new_cart = Cart(id_cart = id_cart, user_cart = user_profile.id_profile, product_cart = id, quantity = quality, status_cart = 1, date_cart_up = current_datetime)
                            db.session.add(new_cart)
                            db.session.commit() 
                        else:
                            pro_exit.quantity += int(quality)
                            db.session.commit()
                        return redirect(url_for('views.cart'))
                    else:
                        check_auth = False
            elif 'view_product' in request.form:
                id_pro = request.form.get('id_product')
                return redirect(url_for('views.shop_single', id = id_pro))
            elif 'add_product' in request.form:
                id_pro = request.form.get('id_product')
                return redirect(url_for('views.shop_single', id = id_pro))
            elif 'like_product' in request.form:
                print("da like")
            elif 'order--pro' in request.form:
                if current_user is not None:
                    if current_user.is_authenticated:
                        if check_view == True:
                            return redirect(url_for('views.dashboards'))
                        else:
                            quality = request.form.get('product-quanity')
                            product_buy = {'id_pro': id, 'quality': quality}
                            return redirect(url_for('views.pay_to_order'))
                    else:
                        check_auth = False
            
            if check_auth == False:
                return redirect(url_for('auth.sign_in')) 
        return render_template("shop-single.html", user=current_user, check_view = check_view, product_list = products, product = product_detail)
    except Exception as e:
        email_error(e)
        return redirect(url_for("views.not_found"))

@views.route('/cart', methods=['GET', 'POST'])
def cart():
    global check_view, product_buy, order_list, pay_1_pro, pay_info, check_del
    cart_product = []
    order_list = []
    pay_1_pro = {}
    pay_info = {}
    try:
        if current_user is not None:   
            if current_user.is_authenticated:
                user_ss = Session.query.filter_by(email_user = current_user.email).first()
                if user_ss.ss_token != session[current_user.email]['token']:           
                    return redirect(url_for("views.sign_out"))
                

                product_buy = {}
                user_profile = Profile.query.filter_by(access_user = user_ss.id_user).first()
                user_cart = Cart.query.filter_by(user_cart = user_profile.id_profile).all()
                
                for item in user_cart:
                    product = Product.query.filter_by(id_product = int(item.product_cart)).first()
                    product_info = {
                    'product': product,
                    'quantity': item.quantity,
                    'status': item.status_cart
                    }
                    cart_product.append(product_info)
                    if item.status_cart == 2:
                        order_info = Order.query.filter_by(cart_pay = item.id_cart).first()
                        status_info = StatusOrder.query.filter_by(id_status = order_info.status_order).first()
                        product = Product.query.filter_by(id_product = item.product_cart).first()

                        order = {
                            'id_pro': product.id_product,
                            'name_product': product.name_product,
                            'img_product': product.img_product,
                            'status_order': status_info.content_status,
                            'date_pay': order_info.date_pay.strftime("%H:%M %d/%m/%Y"),
                            'address_des': order_info.address_des,
                            'total_price':  item.quantity * product.price
                        }

                        order_list.append(order)

                if request.method == 'POST':
                    if 'pay-cart' in request.form:
                        for item in user_cart:
                            if item.status_cart == 1:
                                return redirect(url_for('views.pay'))
                    elif 'cancel_order' in request.form:
                        print("Hủy đơn hàng") 
                
            else:
                return redirect(url_for('auth.sign_in'))
        else: 
            return redirect(url_for('auth.sign_in'))
        return render_template("cart.html",user=current_user, check_view = check_view, product_list = cart_product, order_list = order_list, re_pro_cart = check_del['check'])
    except:
        return redirect(url_for("views.not_found")) 

check_del = {'check': False, 'item': None}

@views.route('/cart/<id>', methods=['GET', 'POST'])
def cart_del(id):
    global check_view, check_del
    if current_user is not None:   
        if current_user.is_authenticated:
            user_ss = Session.query.filter_by(email_user = current_user.email).first()
            if user_ss.ss_token != session[current_user.email]['token']:           
                return redirect(url_for("views.sign_out"))
    if id.isdigit():
        pro_cart = Cart.query.filter_by(product_cart = int(id)).all()
        if pro_cart is not None:
            for item in pro_cart:
                if item.status_cart == 1:
                    db.session.delete(item)
                    db.session.commit()
    else:
        return redirect(url_for('views.not_found'))

    return redirect(url_for('views.cart'))

@views.route('/pay-cart', methods=['GET', 'POST'])
def pay():
    global order_list, pay_info

    if current_user is not None:   
        if current_user.is_authenticated:
            user_ss = Session.query.filter_by(email_user = current_user.email).first()
            if user_ss.ss_token != session[current_user.email]['token']:           
                return redirect(url_for("views.sign_out"))
    
    product_cart = []
    if current_user.is_authenticated:
        user_profile = Profile.query.filter_by(access_user = user_ss.id_user).first()
        user_cart = Cart.query.filter_by(user_cart = user_profile.id_profile).all()
        total_all = 0
        for item in user_cart:
            total_price = 0
            if item.status_cart == 1:
                product = Product.query.filter_by(id_product = int(item.product_cart)).first()
                total_price += product.price * item.quantity
                total_all += product.price * item.quantity
                product_info = {
                    'id_cart': item.id_cart,
                    'total_price': total_price
                } 
                product_cart.append(product_info)
        if total_price == 0:
            print("No products found1")
            return redirect(url_for('views.not_found'))    
        if request.method == 'POST':
            token_auth = request.form.get('token_id')
            name = request.form.get('name')
            phone = request.form.get('phone')
            email = request.form.get('email')
            city_address = request.form.get('city_address')
            note_address = request.form.get('note_address')
            pay = request.form.get('bankcode')
            card_number = request.form.get('card_number')
            date_expired = request.form.get('date_HH')
            cvv_cvc = request.form.get('cvc_cvv')
            check_pay_off = request.form.get('check_pay_off')

            data_time = {}

            if user_ss.ss_token != token_auth:
                return redirect(url_for('views.not_found2'))

            if check_special_chars(note_address) == True:
                data_time = {'name': name, 'phone': phone, 'email': email}

                return render_template("pay.html",user=current_user, check_view = check_view, total_price = total_all, data_time = data_time, charValid = True)

            
            if city_address == "0":
                data_time = {'name': name, 'phone': phone, 'email': email, 'note_address':note_address}
                return render_template("pay.html",user=current_user, check_view = check_view, total_price = total_all, data_time = data_time, check_err=True)
            
            if pay != "default":
                card_info = CardPay.query.filter_by(id_card = card_number, cvc_cvv = int(cvv_cvc), name_card = pay, date_expired = date_expired).first()
                if card_info:
                    pay_info = {'name': name, 'phone': phone, 'email': email, 'city_address': city_address,
                                 'note_address': note_address, 'pay_name': pay, 'card_number': card_number, 'date_expired': date_expired, 'cvv_cvc':cvv_cvc, 'total_price' :total_all, 'check_pay_off': False}
                    data_time = {}

                    status = 1
                    pay_method = "Ngân hàng " + pay
                  
                    for item in product_cart:
                        order_info = {'user_pay': user_profile.id_profile, 'status': status, 'pay_method': pay_method, 'total_price': item['total_price'], 'cart_pay': item['id_cart'], 'check_order': 2}
                        order_list.append(order_info)

                    verification_code = generate_verification_code()
                    # verification_code = "abc123"  # For testing purposes
                    code_verify[current_user.email] = {'code': verification_code, 'pay_confirm': True}
                    email_notice(email_ssmtp, password_ssmtp, session[current_user.email]['email'], verification_code)     
                    return redirect(url_for('views.pay_confirm')) 
                
                else:
                    data_time = {'name': name, 'phone': phone, 'email': email, 'note_address':note_address}
                    return render_template("pay.html",user=current_user, check_view = check_view, total_price = total_all, data_time = data_time, isValid = True)
            else:
                print("Not finished")

            if check_pay_off:
                order_list = []
                pay_info = {'name': name, 'phone': phone, 'email': email, 'city_address': city_address,
                                 'note_address': note_address, 'pay_name':'Chọn ngân hàng thanh toán', 'check_pay_off': True, 'total_price' :total_all}
                
                status = 1
                pay_method = f"Thanh toán khi nhận hàng"
                    
                for item in product_cart:
                    order_info = {'user_pay': user_profile.id_profile, 'status': status, 'pay_method': pay_method, 'total_price': item['total_price'], 'cart_pay': item['id_cart'], 'check_order': 2}
                    order_list.append(order_info)
                verification_code = generate_verification_code()
                # verification_code = "abc123"  # For testing purposes
                code_verify[current_user.email] = {'code': verification_code, 'pay_confirm': True}
                email_notice(email_ssmtp, password_ssmtp, session[current_user.email]['email'], verification_code)
                return redirect(url_for('views.pay_confirm')) 

    else:
        return redirect(url_for('auth.sign_in'))
    
    return render_template("pay.html",user=current_user, check_view = check_view, total_price = total_all, token = session[current_user.email]['token'])

@views.route('/pay-cart/to_buy', methods=['GET', 'POST'])
def pay_to_order():
    global check_view, pay_1_pro, pay_info, order_list, product_buy

    if current_user is not None:   
        if current_user.is_authenticated:
            user_ss = Session.query.filter_by(email_user = current_user.email).first()
            if user_ss.ss_token != session[current_user.email]['token']:           
                return redirect(url_for("views.sign_out"))
    
    if current_user.is_authenticated:
        user_profile = Profile.query.filter_by(access_user = user_ss.id_user).first()
        if 'id_pro' not in product_buy: 
            return redirect(url_for('views.sesion_expires'))
        id_pro = int(product_buy['id_pro'])
        id_qual = int(product_buy['quality'])
        product = Product.query.filter_by(id_product = id_pro).first()
        if product is not None:
            total_price = product.price * id_qual
        else:
            return redirect(url_for('views.not_found'))
        if request.method == 'POST':
            name = request.form.get('name')
            phone = request.form.get('phone')
            email = request.form.get('email')
            city_address = request.form.get('city_address')
            note_address = request.form.get('note_address')
            pay = request.form.get('bankcode')
            card_number = request.form.get('card_number')
            dateHH = request.form.get('date_expired')
            cvv_cvc = request.form.get('cvc_cvv')
            check_pay_off = request.form.get('check_pay_off')

            data_time = {}
            
            if city_address == "0":
                data_time = {'name': name, 'phone': phone, 'email': email, 'note_address':note_address}
                return render_template("pay.html",user=current_user, check_view = check_view, total_price = total_price, data_time = data_time, check_err=True)
            
            if pay != "default":
                card_info = CardPay.query.filter_by(id_card = card_number, name_card = pay, date_expired = dateHH, cvc_cvv = int(cvv_cvc)).first()
                if card_info:
                    order_list = []
                    pay_info = {'name': name, 'phone': phone, 'email': email, 'city_address': city_address,
                                 'note_address': note_address, 'pay_name': pay, 'card_number': card_number, 'date_expired': dateHH, 'cvv_cvc':cvv_cvc, 'total_price' :total_price, 'check_pay_off': False}
                    data_time = {}

                    status = 1
                    pay_method = "Ngân hàng " + pay

                    current_datetime = datetime.now()
                    formatted_time = current_datetime.strftime("%H%S%M%d")
                    id_cart = f'{user_profile.id_profile}_{id_pro}_{formatted_time}'

                    pay_1_pro = {
                        'product': product,
                        'quantity': id_qual,
                        'id_cart': id_cart
                    }

                    order_info = {'user_pay': user_profile.id_profile, 'status': status, 'pay_method': pay_method, 'total_price': total_price, 'cart_pay': id_cart, 'check_order': 2}
                    order_list.append(order_info)

                    verification_code = generate_verification_code()
                    # verification_code = "abc123"  # For testing purposes
                    code_verify[current_user.email] = {'code': verification_code, 'pay_confirm': True}
                    email_notice(email_ssmtp, password_ssmtp, session[current_user.email]['email'], verification_code)        
                    return redirect(url_for('views.pay_confirm')) 
                
                else:
                    data_time = {'name': name, 'phone': phone, 'email': email, 'note_address':note_address}
                    return render_template("pay.html",user=current_user, check_view = check_view, total_price = total_price, data_time = data_time, isValid = True)
            else:
                print("no")
            
            if check_pay_off:
                order_list = []
                pay_info = {'name': name, 'phone': phone, 'email': email, 'city_address': city_address,
                                 'note_address': note_address, 'pay_name':'Chọn ngân hàng thanh toán', 'check_pay_off': True, 'total_price' :total_price}
                

                current_datetime = datetime.now()
                formatted_time = current_datetime.strftime("%H%S%M%d")
                id_cart = f'{user_profile.id_profile}_{id_pro}_{formatted_time}'

                pay_1_pro = {
                        'product': product,
                        'quantity': int(id_qual),
                        'id_cart': id_cart
                    }

                status = 1
                pay_method = f"Thanh toán khi nhận hàng"
                

                order_info = {'user_pay': user_profile.id_profile, 'status': status, 'pay_method': pay_method, 'total_price': total_price, 'cart_pay': id_cart, 'check_order': 2}
                order_list.append(order_info)

                verification_code = generate_verification_code()
                # verification_code = "abc123"  # For testing purposes
                code_verify[current_user.email] = {'code': verification_code, 'pay_confirm': True}
                email_notice(email_ssmtp, password_ssmtp, session[current_user.email]['email'], verification_code)
                
                return redirect(url_for('views.pay_confirm')) 

    else:
        order_list = []
        pay_1_pro = {}
        return redirect(url_for('auth.sign_in'))
    return render_template("pay.html",user=current_user, check_view = check_view, total_price = total_price)

@views.route('/pay-confirm', methods=['GET', 'POST'])
def pay_confirm():
    global check_view, pay_1_pro, order_list, pay_info, product_buy
    
    if current_user is not None:   
        if current_user.is_authenticated:
            user_ss = Session.query.filter_by(email_user = current_user.email).first()
            if user_ss.ss_token != session[current_user.email]['token']:           
                return redirect(url_for("views.sign_out"))
    
    check_error = False
    cart_product = []
    if current_user.is_authenticated:
        try:
            if len(order_list) > 0:
                user_profile = Profile.query.filter_by(access_user = user_ss.id_user).first()
                user_cart = Cart.query.filter_by(user_cart = user_profile.id_profile).all()
                
                if pay_1_pro:
                    cart_product.append(pay_1_pro)
                for item in user_cart:
                    if order_list[0]['check_order'] == 1:
                        products = Product.query.filter_by(id_product = order_list[0]['id_pro']).first()
                        product_info = {
                        'product': products,
                        'quantity': item.quantity
                        }
                        cart_product.append(product_info)
                    elif order_list[0]['check_order'] == 2 and item.status_cart == 1:
                        products = Product.query.filter_by(id_product = int(item.product_cart)).first()
                        product_info = {
                        'product': products,
                        'quantity': item.quantity
                        }
                        cart_product.append(product_info)
            if request.method == 'POST':
                try:
                    code = request.form.get('code--verify')
                    if code_verify and pay_info:
                        if code == code_verify[current_user.email]['code']:
                            if pay_1_pro:
                                current_datetime = datetime.now()
                                new_cart = Cart(id_cart = pay_1_pro['id_cart'], user_cart = user_profile.id_profile, product_cart = pay_1_pro['product'].id_product, quantity = pay_1_pro['quantity'], status_cart = 2, date_cart_up = current_datetime)
                                db.session.add(new_cart)
                                db.session.commit() 
                            for item in order_list:
                                check_order = Order.query.filter_by(cart_pay = item['cart_pay']).first()
                                if check_order:
                                    check_order.total_price += item['total_price']
                                    db.session.commit()
                                else:
                                    current_datetime = datetime.now()
                                    get_id = Order.query.order_by(Order.id_order.desc()).first()
                                    if get_id is None:
                                        id = 0
                                    else:
                                        id = get_id.id_order
                                    
                                    new_id = id + 1
                                    new_order = Order(id_order = new_id, date_pay = current_datetime, user_pay=item['user_pay'], status_order = item['status'], pay_method = item['pay_method'], total_price = item['total_price'], address_des = f"{pay_info['note_address']}, {pay_info['city_address']}", phone = pay_info['phone'], cart_pay = item['cart_pay'])
                                    db.session.add(new_order)
                                    db.session.commit()
                                
                                

                            if pay_info['check_pay_off'] == False :
                                user_profile.info_card = pay_info['card_number']
                                db.session.commit()
                            for item in user_cart:
                                item.status_cart = 2
                                db.session.commit()

                            product_buy = {}
                            return redirect(url_for('views.cart'))                     
                        else:
                            check_error = True
                    else:
                        return redirect(url_for('views.not_found'))
                except Exception as e:
                    email_error(e)
                    return redirect(url_for("views.not_found"))
        except:
            email_notice(session)
            return redirect(url_for('views.not_found'))
    else:
        return redirect(url_for('auth.sign_in'))
    return render_template("pay-confirm.html",user=current_user, check_view = check_view, product_list = cart_product, pay_info = pay_info, check_error = check_error)
    

@views.route('/about', methods=['GET', 'POST'])
def about():
    if current_user is not None:   
        if current_user.is_authenticated:
            user_ss = Session.query.filter_by(email_user = current_user.email).first()
            if user_ss.ss_token != session[current_user.email]['token']:           
                return redirect(url_for("views.sign_out"))
    return render_template("about.html",user=current_user, check_view = check_view)

@views.route('/contact', methods=['GET', 'POST'])
def contact():
    if current_user is not None:   
        if current_user.is_authenticated:
            user_ss = Session.query.filter_by(email_user = current_user.email).first()
            if user_ss.ss_token != session[current_user.email]['token']:           
                return redirect(url_for("views.sign_out"))
    return render_template("contact.html",user=current_user, check_view = check_view)

@views.route('/profile-user', methods=['GET', 'POST'])
def profile_user():
    if current_user is not None:   
        if current_user.is_authenticated:
            user_ss = Session.query.filter_by(email_user = current_user.email).first()
            if user_ss.ss_token != session[current_user.email]['token']:           
                return redirect(url_for("views.sign_out"))
    return render_template("profile_user.html",user=current_user,email = session[current_user.email]['email'], check_view = check_view)


#--------------------- manager - AIShop

# ------- Dashboards - model

@views.route('/dashboards', methods=['GET', 'POST'])
def dashboards(): 
    global check_view
    products = db.session.query(Product).all()
    if current_user.is_authenticated:
        if current_user.user_access == 'sysadm01':
            user_ss = Session.query.filter_by(email_user = current_user.email).first()
            if user_ss.ss_token != session[current_user.email]['token']:           
                return redirect(url_for("views.sign_out")) 
            user_profile = Profile.query.filter_by(access_user = user_ss.id_user).first()
            products = db.session.query(Product).all()
            return render_template("manager-product.html", user=user_profile, product_list = products)
    return render_template("index.html",user=current_user, product_list = products, check_view = check_view)

# ------- Products - model

@views.route('/products', methods=['GET', 'POST'])
def products():
    global check_view
    products = db.session.query(Product).all()
    if current_user.is_authenticated:
        if current_user.user_access == 'sysadm01':
            user_ss = Session.query.filter_by(email_user = current_user.email).first()
            if user_ss.ss_token != session[current_user.email]['token']:           
                return redirect(url_for("views.sign_out")) 
            user_profile = Profile.query.filter_by(access_user = user_ss.id_user).first()
            return render_template("ecommerce-products.html",user=current_user, user_profile=user_profile, product_list = products)
    return render_template("index.html",user=current_user, product_list = products, check_view = check_view)

@views.route('/products/<number>', methods=['GET', 'POST'])
def products_del(number):
    global check_view
    products = db.session.query(Product).all()
    if current_user.is_authenticated:
        if current_user.user_access == 'sysadm01':
            user_ss = Session.query.filter_by(email_user = current_user.email).first()
            if user_ss.ss_token != session[current_user.email]['token']:           
                return redirect(url_for("views.sign_out")) 
            if number.isdigit():
                product = Product.query.filter_by(id_product = int(number)).first()
                if product is not None:
                    db.session.delete(product)
                    db.session.commit()
                else:
                    return redirect(url_for(('views.not_found')))
            else:
                return redirect(url_for(('views.not_found')))
            return render_template("ecommerce-products.html", user = current_user, product_list = products)
    return render_template("index.html",user=current_user, product_list = products, check_view = check_view)

@views.route('/products/product-details/<number>', methods=['GET', 'POST'])
def product_details(number):
    global check_view
    if current_user.is_authenticated:
        if current_user.user_access == 'sysadm01':
            user_ss = Session.query.filter_by(email_user = current_user.email).first()
            if user_ss.ss_token != session[current_user.email]['token']:           
                return redirect(url_for("views.sign_out")) 
            if number.isdigit():
                product = Product.query.filter_by(id_product = int(number)).first()
                if product is not None:
                    productName = request.form.get('productName')
                    trademark = request.form.get('trademark')
                    priceName = request.form.get('priceName')
                    description = request.form.get('description')
                    url_img = request.form.get('url_img')
                    check = False
                    if request.method == 'POST':
                        productName1 = request.form.get('productName')
                        trademark1 = request.form.get('trademark')
                        priceName1 = request.form.get('priceName')
                        description1 = request.form.get('description')
                        url_img1 = request.form.get('url_img')                        
                        if productName1 != productName:
                            product.name_product = productName1
                            db.session.commit()
                            check = True
                        if trademark1 != trademark:
                            product.trademark = trademark1
                            db.session.commit()
                            check = True
                        if priceName1 != priceName:
                            product.price = priceName1
                            db.session.commit()
                            check = True
                        if description1 != description:
                            product.describe = description1
                            db.session.commit()
                            check = True
                        if url_img1 != url_img:
                            if url_img1 is None:
                                url_img1 = "/assets/img/400x400/img2.jpg"
                            else:
                                file_extension = ["png", "jpg", "jpeg"]
                                url_img1 = url_img1.split('.')[-1] 
                            if url_img not in file_extension: 
                                pro_his = {'productName': productName, 'trademark': trademark, 'priceName': priceName, 'description': description}
                                return render_template("ecommerce-product-details.html", user = current_user, user_profile = user_profile, pro_his = pro_his)
                            product.img_product = url_img1
                            db.session.commit()
                            check = True

                        if check == True:
                            return redirect(url_for('views.products'))
                    user_profile = Profile.query.filter_by(access_user = user_ss.id_user).first()
                    return render_template("ecommerce-product-details.html",user=current_user, user_profile=user_profile, product = product)
                else:
                    return redirect(url_for(('views.not_found')))
            else:
                return redirect(url_for(('views.not_found')))
    return render_template("index.html",user=current_user, product_list = products, check_view = check_view)

@views.route('/products/add-product', methods=['GET', 'POST'])
def product_add():
    global check_view
    if current_user.is_authenticated:
        if current_user.user_access == 'sysadm01':  
            user_ss = Session.query.filter_by(email_user = current_user.email).first()
            if user_ss.ss_token != session[current_user.email]['token']:           
                return redirect(url_for("views.sign_out")) 
            user_profile = Profile.query.filter_by(access_user = user_ss.id_user).first()  
            if request.method == 'POST':
                productName = request.form.get('productName')
                trademark = request.form.get('trademark')
                priceName = request.form.get('priceName')
                description = request.form.get('description')
                url_img = request.form.get('url_img')

                if url_img is None:
                    url_img = "/assets/img/400x400/img2.jpg"
                else:
                    file_extension = ["png", "jpg", "jpeg"]
                    url_img = url_img.split('.')[-1] 
                    if url_img in file_extension: 
                        url_img = "/assets/img/pro_img/"+url_img
                    else:
                        pro_his = {'productName': productName, 'trademark': trademark, 'priceName': priceName, 'description': description}
                        return render_template("ecommerce-add-product.html", user = current_user, user_profile = user_profile, pro_his = pro_his)
                get_id = Product.query.order_by(Product.id_product.desc()).first()
                if get_id is None:
                    id = 0
                else:
                    id = get_id.id_product
                new_id = id + 1
                description = remove_special_chars(description)
                try:
                    new_product = Product(id_product= new_id,img_product=url_img, name_product = productName, trademark=trademark,status_product=1, price=priceName, describe=description, review=0)
                    db.session.add(new_product)
                    db.session.commit()
                    return redirect(url_for('views.products', user = current_user, user_profile = user_profile)) 
                except:
                    return redirect(url_for('views.not_found'))

            return render_template("ecommerce-add-product.html", user = current_user, user_profile = user_profile)
        else:
            return redirect(url_for('views.home'))
    return redirect(url_for('auth.sign_in'))    

@views.route('/orders', methods=['GET', 'POST'])
def orders():
    global check_view
    if current_user.is_authenticated:
        if current_user.user_access == 'sysadm01':
            user_ss = Session.query.filter_by(email_user = current_user.email).first()
            if user_ss.ss_token != session[current_user.email]['token']:           
                return redirect(url_for("views.sign_out")) 
            user_profile = Profile.query.filter_by(access_user = user_ss.id_user).first()
            order_list = []
            order_info = db.session.query(Order).all()
            for item in order_info:
                
                user_profile = Profile.query.filter_by(id_profile = item.user_pay).first()
                status_info = StatusOrder.query.filter_by(id_status = item.status_order).first()

                order = {
                    'id_order': item.id_order,
                    'date_pay': item.date_pay.strftime("%H:%M %d/%m/%Y"),
                    'user_pay': user_profile.phone_number,
                    'status_order': status_info.content_status,
                    'pay_method': item.pay_method,
                    'total_price': item.total_price,
                    'address_des': item.address_des
                }

                order_list.append(order) 
            if request.method == 'POST':
                if len(order_list) == 0:
                    return render_template("ecommerce-orders.html", user = current_user, check_view = check_view, order_list = order_list, user_profile = user_profile)
                try:
                    df = pd.DataFrame(order_list)
                    df.to_excel(r'Desktop/', index=False)
                except:
                    return redirect(url_for('views.not_found'))
        else:
            return redirect(url_for('views.home'))
    else:
          return redirect(url_for('auth.sign_in'))
    return render_template("ecommerce-orders.html", user = current_user, check_view = check_view, order_list = order_list, user_profile = user_profile)  

@views.route('/orders/order-details/<id>', methods=['GET', 'POST'])
def order_details(id):
    global check_view
    if current_user.is_authenticated:
        if current_user.user_access == 'sysadm01':
            user_ss = Session.query.filter_by(email_user = current_user.email).first()
            if user_ss.ss_token != session[current_user.email]['token']:           
                return redirect(url_for("views.sign_out")) 
            if id.isdigit():
                order_info = Order.query.filter_by(id_order = int(id)).first()
                if order_info is None:
                    return redirect(url_for('views.not_found'))
                user_profile = Profile.query.filter_by(id_profile = order_info.user_pay).first()
                status_info = StatusOrder.query.filter_by(id_status = order_info.status_order).first()

                user_cart = Cart.query.filter_by(id_cart = order_info.cart_pay).first()
                product = Product.query.filter_by(id_product = user_cart.product_cart).first()
            
                product_info = {
                    'img_pro': product.img_product,
                    'name_pro': product.name_product,
                    'price': product.price,
                    'quantity': user_cart.quantity,
                    'total_price': order_info.total_price
                }
                date_pay = order_info.date_pay.strftime("%H:%M %d/%m/%Y")

                date_format = "%H:%M %d/%m/%Y"
                order_info_date_pay = datetime.strptime(date_pay, date_format)
                date_del = order_info_date_pay + timedelta(days=4)
                card_pay = "0"
                if user_profile.info_card is not None:
                    card_pay = user_profile.info_card[-4:]
                order_info = {
                    'id_order': id,
                    'date_pay': order_info_date_pay,
                    'date_del': date_del,
                    'user_avatar': user_profile.avatar,
                    'user_name': user_profile.name_user,
                    'phone_contact': order_info.phone,
                    'card_pay': card_pay,
                    'status_order': status_info.content_status,
                    'pay_method': order_info.pay_method,
                    'address_des': order_info.address_des
                }


                if request.method == 'POST':
                    df = pd.DataFrame(order_info)

                    df.to_excel(r'Desktop/', index=False)

        else:
            return redirect(url_for('views.home'))
    else:
          return redirect(url_for('auth.sign_in'))
    return render_template("ecommerce-order-details.html", user = current_user, user_profile = user_profile, check_view = check_view, order = order_info, product = product_info)  

@views.route('/welcome-pages', methods=['GET', 'POST'])
def welcome_pages():
    global check_view
    products = db.session.query(Product).all()
    if current_user.is_authenticated:
        if current_user.user_access == 'sysadm01':
            user_ss = Session.query.filter_by(email_user = current_user.email).first()
            if user_ss.ss_token != session[current_user.email]['token']:           
                return redirect(url_for("views.sign_out")) 
            check_view = True
            products = db.session.query(Product).all()
            return render_template("/index.html", user = current_user, check_view = check_view, product_list = products)
    return render_template("index.html",user=current_user, product_list = products, check_view = check_view)    
