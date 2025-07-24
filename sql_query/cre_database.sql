
----------------- Create Database AIShop Website

CREATE TABLE PERMISSION (
    id_access VARCHAR(50) PRIMARY KEY
);

CREATE TABLE STATUS_LOGIN (
    id_login VARCHAR(50) NOT NULL PRIMARY KEY,
    date_user_cre TIMESTAMP NOT NULL,
    date_pass_res TIMESTAMP NULL
);

CREATE TABLE ACCOUNT_LOGIN(
    email VARCHAR(250) PRIMARY KEY NOT NULL,
    passwd VARCHAR(250) NOT NULL,
    user_access VARCHAR(50) NOT NULL,
	user_status VARCHAR(50) NOT NULL,
	login_failed INT NOT NULL,
    FOREIGN KEY (user_access) REFERENCES PERMISSION (id_access) ON DELETE NO ACTION ON UPDATE NO ACTION,
	FOREIGN KEY (user_status) REFERENCES STATUS_LOGIN (id_login) ON DELETE NO ACTION ON UPDATE CASCADE
);

CREATE TABLE SESSION_LOGIN (
    id_user VARCHAR(50) PRIMARY KEY NOT NULL,
    email_user VARCHAR(250) NOT NULL,
	date_login_rec TIMESTAMP NOT NULL,
	ss_token VARCHAR(150) NULL,
	FOREIGN KEY (email_user) REFERENCES ACCOUNT_LOGIN (email) ON DELETE NO ACTION ON UPDATE CASCADE
);

CREATE TABLE CARD_PAY (
	id_card VARCHAR(50) PRIMARY KEY NOT NULL,
	cvc_cvv INT NOT NULL,
	name_card VARCHAR(100) NOT NULL,
	date_expired VARCHAR(15) NOT NULL,
	email_address VARCHAR(250) NULL
);

CREATE TABLE PROFILE_USER (
    id_profile VARCHAR(50) NOT NULL PRIMARY KEY,
    name_user VARCHAR(50) NULL,
    avatar VARCHAR(350) NULL,
	phone_number VARCHAR(25) NULL,
	address VARCHAR(350) NULL,
	access_user VARCHAR(50) NOT NULL,
	info_card VARCHAR(50) NULL,
	FOREIGN KEY (access_user) REFERENCES SESSION_LOGIN (id_user) ON DELETE NO ACTION ON UPDATE CASCADE,
	FOREIGN KEY (info_card) REFERENCES CARD_PAY (id_card) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE INFO_PRODUCT (
    id_product INT PRIMARY KEY NOT NULL,
	img_product VARCHAR(250) NULL,
    name_product VARCHAR(300) NOT NULL,
	trademark VARCHAR(50) NOT NULL,
	status_product INT NOT NULL,
    price INT NOT NULL,
	describe VARCHAR(350) NULL,
	review INT NULL,
	num_selled INT DEFAULT 0 NOT NULL
);

CREATE TABLE STATUS_CART (
	id_status INT PRIMARY KEY NOT NULL,
	content_status VARCHAR(50) NOT NULL
);

CREATE TABLE CART (
    id_cart VARCHAR(50) NOT NULL PRIMARY KEY,
    user_cart VARCHAR(50) NULL,
    product_cart INT NULL,
    quantity INT NOT NULL,
	status_cart INT NULL,
	date_cart_up TIMESTAMP NULL,
    FOREIGN KEY (user_cart) REFERENCES PROFILE_USER (id_profile) ON DELETE SET NULL ON UPDATE CASCADE,
	FOREIGN KEY (status_cart) REFERENCES STATUS_CART (id_status) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (product_cart) REFERENCES INFO_PRODUCT (id_product) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE STATUS_ORDER (
	id_status INT PRIMARY KEY NOT NULL,
	content_status VARCHAR(50) NOT NULL
);

CREATE TABLE INFO_ORDER (
	id_order INT PRIMARY KEY NOT NULL,
	date_pay TIMESTAMP NOT NULL,
    user_pay VARCHAR(50) NOT NULL,
	status_order INT NOT NULL,
	pay_method VARCHAR(25) NOT NULL,
	total_price INT NOT NULL,
	address_des VARCHAR(50) NOT NULL,
	phone VARCHAR(15) NOT NULL,
	cart_pay VARCHAR(50) NULL,
    FOREIGN KEY (cart_pay) REFERENCES CART (id_cart) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (status_order) REFERENCES STATUS_ORDER (id_status) ON DELETE NO ACTION ON UPDATE CASCADE
);


-----/   Step 3: Create default value to table (Permission, Product, Info Card, Status Card, Status Order)

INSERT INTO permission(id_access) VALUES ('sysadm01');
INSERT INTO permission(id_access) VALUES ('syscus02');

INSERT INTO INFO_PRODUCT(id_product, img_product, name_product, trademark, status_product, price, describe, review) VALUES (1, N'/assets/img/pro_img/Son Kem Lì Bbia.png', N'Son Kem Lì Bbia Last Velvet Lip Tint Version 5 (5 màu) 5g Bbia Official Store', N'Bbia', 1, 199000, N'Son kem lỳ Bbia Last Velvet Lip Tint là dòng son lỳ với độ bám dính cực cao, hút vào môi bạn như nam châm và lên màu rõ ràng chỉ sau một lần thoa',152);
INSERT INTO INFO_PRODUCT(id_product, img_product, name_product, trademark, status_product, price, describe, review) VALUES (2, N'/assets/img/pro_img/Son Tint Lì Rom&nd.png', N'Son Tint Lì Rom&nd', N'Rom&nd', 1, 290000, N'Romand là thương hiệu mỹ phẩm đến từ Hàn Quốc ra mắt vào năm 2017, hướng đến phong cách trẻ trung và năng động. Các sản phẩm từ nhà Romand luôn tạo được tiếng vang và nhận được sự yêu thích nồng nhiệt vì giá thành hợp lý, chất lượng ưng ý và luôn dẫn đầu các xu hướng mới lạ',14);
INSERT INTO INFO_PRODUCT(id_product, img_product, name_product, trademark, status_product, price, describe, review) VALUES (3, N'/assets/img/pro_img/Son lì Colorkey Soft Matte Water Tint.png', N'Son lì Colorkey Soft Matte Water Tint', N'Colorkey', 1, 358000, N'Son môi COLORKEY Kolaki màu bóng mờ không dính cốc ánh gương 1.8g',1222);
INSERT INTO INFO_PRODUCT(id_product, img_product, name_product, trademark, status_product, price, describe, review) VALUES (4, N'/assets/img/pro_img/Gel rửa mặt ngăn ngừa mụn Truesky Centella Cleanser.png', N'Gel rửa mặt ngăn ngừa mụn Truesky Centella Cleanser', N'Truesky', 1, 548000, N'Làm sạch da, loại bỏ tế bào da chết, điều tiết dầu nhờn, hạn chế quá trình hình thành m.ụ.n, hỗ trợ ngừa mụn, ức chế sự tăng trưởng của các loại vi khuẩn gây mụn',7);
INSERT INTO INFO_PRODUCT(id_product, img_product, name_product, trademark, status_product, price, describe, review) VALUES (5, N'/assets/img/pro_img/Kem Nền Mịn Nhẹ Kiềm Dầu Fit Me Maybelline New York Matte Poreless Foundation 30ml.png', N'Kem Nền Mịn Nhẹ Kiềm Dầu Fit Me Maybelline New York Matte', N'Simple', 1, 176800, N'Sữa rửa mặt Simple Refreshing lành tính sạch thoáng - cho da nhạy cảm chứa X2 Vitamin B5*, Vitamin E và Pro Amino Acids giúp làm sạch da hiệu quả, cuốn đi chất nhờn, bụi bẩn và các tạp chất khác và không gây kích ứng, cho da mềm mịn, đồng thời mang lại cảm giác tươi mát và sạch thoáng cho da',657);
INSERT INTO INFO_PRODUCT(id_product, img_product, name_product, trademark, status_product, price, describe, review) VALUES (6, N'/assets/img/pro_img/Kem nền kiềm dầu Catrice HD 24h Liquid Coverage Foundation che phủ hoàn hảo.png', N'Kem nền kiềm dầu Catrice HD 24h Liquid Coverage', N'Maybelline New York', 1, 900000, N'Kem nền Fit Me gây ấn tượng với khả năng kiềm dầu cho lớp nền mịn lì tự nhiên, đồng thời che phủ tốt mọi khuyết điểm trên bề mặt da và che phủ hoàn hảo lỗ chân lông. Dòng kem nền Fit Me có 12 tông màu phù',9045);
INSERT INTO INFO_PRODUCT(id_product, img_product, name_product, trademark, status_product, price, describe, review) VALUES (7, N'/assets/img/pro_img/Kem Chống Nắng LOreal.png', N'Kem Chống Nắng LOreal', N'Catrice', 1, 150000, N'Với chị em gái yêu thích vẻ tự nhiên thì Kem Nền Kiềm Dầu - Catrice HD Liquid Coverage Foundation là một dòng kem nền hoàn hảo, giá lại rất phải chăng, có mùi thơm dịu nhẹ. Tạo một lớp nền mỏng, đều màu, trong suốt',10452);

INSERT INTO CARD_PAY(id_card, cvc_cvv, name_card, date_expired) VALUES ('5200000000001005', 123, 'MASTERCARD', '12/23');
INSERT INTO CARD_PAY(id_card, cvc_cvv, name_card, date_expired) VALUES ('5200000000001096', 123, 'MASTERCARD', '12/23');
INSERT INTO CARD_PAY(id_card, cvc_cvv, name_card, date_expired) VALUES ('3337000000000008', 123, 'JCB', '12/23');
INSERT INTO CARD_PAY(id_card, cvc_cvv, name_card, date_expired) VALUES ('3337000000200004', 123, 'JCB', '12/23');
INSERT INTO CARD_PAY(id_card, cvc_cvv, name_card, date_expired) VALUES ('4456530000001096', 123, 'VISA', '12/23');
INSERT INTO CARD_PAY(id_card, cvc_cvv, name_card, date_expired) VALUES ('4456530000001005', 123, 'VISA', '12/23');
INSERT INTO CARD_PAY(id_card, cvc_cvv, name_card, date_expired) VALUES ('9704195798459170488', 123, 'NCB', '12/23');
INSERT INTO CARD_PAY(id_card, cvc_cvv, name_card, date_expired) VALUES ('9704198526191432198', 123, 'NCB', '07/15');
INSERT INTO CARD_PAY(id_card, cvc_cvv, name_card, date_expired) VALUES ('9704192181368742', 123, 'NCB', '07/15');
INSERT INTO CARD_PAY(id_card, cvc_cvv, name_card, date_expired) VALUES ('9704193370791314', 123, 'NCB', '07/15');
INSERT INTO CARD_PAY(id_card, cvc_cvv, name_card, date_expired) VALUES ('9704194841945513', 123, 'NCB', '07/15');
INSERT INTO CARD_PAY(id_card, cvc_cvv, name_card, date_expired) VALUES ('9704310005819191', 123, 'EXIMBANK', '10/26');

INSERT INTO STATUS_CART(id_status, content_status) VALUES (1, N'Chưa thanh toán');
INSERT INTO STATUS_CART(id_status, content_status) VALUES (2, N'Đã thanh toán');

INSERT INTO STATUS_ORDER(id_status, content_status) VALUES (1, N'Đang vận chuyển');
INSERT INTO STATUS_ORDER(id_status, content_status) VALUES (2, N'Hoàn tất giao dịch');
