from . import db
from flask_login import UserMixin

#----------------------- Khởi tạo các đối tượng table tương ứng tới các table trong DATABASE

class Permission(db.Model, UserMixin):
    __tablename__ = 'permission'
    id_access = db.Column(db.Unicode(50), primary_key=True)

class Status(db.Model):
    __tablename__ = 'status_login'
    id_login = db.Column(db.Unicode(50), nullable=False, primary_key=True)
    date_user_cre = db.Column(db.DateTime, nullable=False)
    date_pass_res = db.Column(db.DateTime, nullable=True)

class User(db.Model, UserMixin):
    __tablename__ = 'account_login'
    email = db.Column(db.Unicode(250), nullable=False, primary_key=True)
    passwd = db.Column(db.Unicode(250), nullable=False)
    user_access = db.Column(db.Unicode(50), db.ForeignKey('permission.id_access'), nullable=False)
    user_status = db.Column(db.Unicode(50), db.ForeignKey('status_login.id_login'), nullable=False)
    login_failed = db.Column(db.Integer, nullable=False)

    def get_id(self):
        return self.email

class Session(db.Model):
    __tablename__ = 'session_login'
    id_user = db.Column(db.Unicode(50), nullable=False, primary_key=True)
    email_user = db.Column(db.Unicode(250), db.ForeignKey('account_login.email'), nullable=False)
    date_login_rec = db.Column(db.DateTime, nullable=False)
    ss_token = db.Column(db.Unicode(150), nullable=True)

class StatusCart(db.Model):
    __tablename__ = 'status_cart'
    id_status = db.Column(db.Integer, primary_key=True, nullable=True)
    content_status = db.Column(db.Unicode(50), nullable=False)

class Cart(db.Model):
    __tablename__ = 'cart'
    id_cart = db.Column(db.Unicode(50), nullable=False, primary_key=True)
    user_cart = db.Column(db.Unicode(50), nullable=True)
    product_cart = db.Column(db.Integer, nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    status_cart = db.Column(db.Integer, db.ForeignKey('status_cart.id_status'), nullable=True)
    date_cart_up = db.Column(db.DateTime, nullable=True)

class CardPay(db.Model):
    __tablename__ = 'card_pay'
    id_card = db.Column(db.Unicode(50), primary_key=True, nullable=False)
    cvc_cvv = db.Column(db.Integer, nullable=False)
    name_card = db.Column(db.Unicode(100), nullable=False)
    date_expired = db.Column(db.Unicode(15), nullable=False)
    id_user = db.Column(db.Unicode(250), nullable=True)

class Profile(db.Model):
    __tablename__ = 'profile_user'
    id_profile = db.Column(db.Unicode(50), nullable=False, primary_key=True)
    name_user = db.Column(db.Unicode(25), nullable=True)
    avatar = db.Column(db.Unicode(350), nullable=True)
    phone_number = db.Column(db.Unicode(25), nullable=True)
    address = db.Column(db.Unicode(350), nullable=True)
    access_user = db.Column(db.Unicode(50), db.ForeignKey('session_login.id_user'), nullable=False)
    info_card = db.Column(db.Unicode(50), db.ForeignKey('card_pay.id_card'), nullable=True)

class Product(db.Model):
    __tablename__ = 'info_product'
    id_product = db.Column(db.Integer, primary_key=True, server_default='0')
    img_product = db.Column(db.Unicode(250), nullable=True)
    name_product = db.Column(db.Unicode(300), nullable=False)
    trademark = db.Column(db.Unicode(50), nullable=False)
    status_product = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    describe = db.Column(db.Unicode(350), nullable=True)
    review = db.Column(db.Integer, nullable=True)
    num_selled = db.Column(db.Integer, nullable=False)

class StatusOrder(db.Model):
    __tablename__ = 'status_order'
    id_status = db.Column(db.Integer, primary_key=True, nullable=True)
    content_status = db.Column(db.Unicode(50), nullable=False)

class Order(db.Model):
    __tablename__ = 'info_order'
    id_order = db.Column(db.Integer, primary_key=True, server_default='0', nullable=True)
    date_pay = db.Column(db.DateTime, nullable=False)
    user_pay = db.Column(db.Unicode(30), nullable=False)
    status_order = db.Column(db.Integer, db.ForeignKey('status_order.id_status'), nullable=False)
    pay_method = db.Column(db.Unicode(25), nullable=False)
    address_des = db.Column(db.Unicode(350), nullable=False)
    phone = db.Column(db.Unicode(15), nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    cart_pay = db.Column(db.Unicode(50), db.ForeignKey('cart.id_cart'), nullable=False)
