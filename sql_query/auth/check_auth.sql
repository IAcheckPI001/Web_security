

CREATE or REPLACE FUNCTION SP_LOGIN(
    inp_email VARCHAR(250),
    pass VARCHAR(250)
)
RETURNS VARCHAR AS $$
DECLARE
	inp_pass VARCHAR(250);
	access_data VARCHAR(250);
	num_login_failed INT;
BEGIN
    SELECT passwd, login_failed, user_access
    INTO inp_pass, num_login_failed, access_data
    FROM account_login 
    WHERE email = inp_email;
	
	IF inp_pass IS NULL THEN
		RETURN  '-1';
		
	ELSIF inp_pass = pass THEN
		RETURN CASE
			WHEN access_data = 'sysadm01' THEN 'views.dashboards'
			WHEN access_data = 'syscus02' THEN 'views.home'
			ELSE 'Error auth'
		END;
	ELSE 
		RETURN num_login_failed::VARCHAR;
	END IF;
END;
$$ LANGUAGE plpgsql;