import hashlib
import secrets

def create_sha256_hash(data):
    # Chuyển đổi dữ liệu thành định dạng byte trước khi băm
    byte_data = data.encode('utf-8')  # Chuyển đổi chuỗi sang byte (UTF-8 encoding)
    
    # Tạo đối tượng hash SHA-256
    sha256 = hashlib.sha256()
    
    # Cập nhật đối tượng hash với dữ liệu
    sha256.update(byte_data)
    
    # Lấy giá trị hash dưới dạng hex
    hashed_data = sha256.hexdigest()
    
    return hashed_data

def generate_csrf_token():
    token = secrets.token_hex(16)
    return token
