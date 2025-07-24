


CREATE or REPLACE FUNCTION SP_GETPASS(
    inp_email VARCHAR(250),
    pass VARCHAR(250),
	inp_date TIMESTAMP
)
RETURNS VARCHAR AS $$
DECLARE
	inp_pass VARCHAR(250);
	id_status VARCHAR(250);
BEGIN

    SELECT passwd, user_status
    INTO inp_pass, id_status
    FROM ACCOUNT_LOGIN 
    WHERE email = inp_email;
    
	IF inp_pass = pass THEN
		RETURN '-1';
	ELSE 
		BEGIN
			BEGIN
				-- Cập nhật mật khẩu
				UPDATE ACCOUNT_LOGIN 
				SET passwd = pass
				WHERE email = inp_email;

				-- Cập nhật thông tin trạng thái
				UPDATE STATUS_LOGIN
				SET date_pass_res = inp_date
				WHERE id_login = id_status;

				RETURN '1';
			EXCEPTION
				WHEN OTHERS THEN
					RETURN 'Error: ' || SQLERRM;
			END;
		END;
	END IF;
END;
$$ LANGUAGE plpgsql;