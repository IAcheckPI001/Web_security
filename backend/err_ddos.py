from flask import request, abort
import time
import subprocess

# Dictionary để lưu trữ số lượng yêu cầu từ mỗi IP
request_count = {}

# Danh sách IP bị chặn
blocked_ips = set()

# Thời gian giới hạn (giây)
limit_period = 60

# Số lượng yêu cầu tối đa được chấp nhận trong limit_period
max_requests = 10

def add_iptables_rule(ip):
    # Tạo lệnh để thêm quy tắc chặn IP vào IPTables
    command = f"iptables -A INPUT -s {ip} -j DROP"

    # Thực thi lệnh
    subprocess.run(command, shell=True)

def protected_ddos():
    client_ip = request.remote_addr  # Lấy địa chỉ IP của client
    
    # Kiểm tra xem IP có trong danh sách bị chặn không
    if client_ip in blocked_ips:
        abort(403)  # Trả về lỗi 403 - Forbidden nếu IP nằm trong danh sách bị chặn

    # Kiểm tra xem IP đã có trong request_count chưa
    if client_ip not in request_count:
        request_count[client_ip] = [time.time(), 1]  # Nếu chưa có, thêm mới và đếm là 1
    else:
        # Nếu đã có, kiểm tra xem đã qua thời gian giới hạn chưa
        current_time = time.time()
        if current_time - request_count[client_ip][0] > limit_period:
            # Nếu đã vượt quá thời gian giới hạn, reset lại số lượng yêu cầu và thời gian
            request_count[client_ip] = [current_time, 1]
        else:
            # Nếu chưa vượt quá thời gian giới hạn, kiểm tra số lượng yêu cầu
            if request_count[client_ip][1] >= max_requests:
                blocked_ips.add(client_ip)  # Thêm IP vào danh sách bị chặn
                add_iptables_rule(client_ip)

            else:
                # Nếu chưa vượt quá số lượng yêu cầu, tăng biến đếm lên 1
                request_count[client_ip][1] += 1

    return 1