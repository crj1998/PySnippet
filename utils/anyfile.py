import os

def write_file(file_path: str, file_size_bytes: int):
    with open(file_path, 'wb') as file:
        file.write(os.urandom(file_size_bytes))

def read_file(file_path: str):
    with open(file_path, "rb") as file:
        data = file.read()
    return data
    
if __name__ == '__main__':
    # 生成一个大小为1MB的随机数据文件
    file_path = 'data.bin'
    write_file(file_path, 1024 * 1024)
    assert len(read_file(file_path)) == os.path.getsize(file_path)
