"""
pip install pyzipper tqdm
"""
import pyzipper
import itertools
from tqdm import tqdm 
from multiprocessing.pool import Pool

NUM_THREADS = 8

characters = "0123456789"
length = 6
encrypted_zipfile = 'xxxxxxx.zip' 

def unzip(password):
    password = "".join(password)
    with pyzipper.AESZipFile(encrypted_zipfile, 'r', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zipfile:
        try:
            zipfile.extractall(pwd=password.encode())
            return password, True
        except:
            return password, False

def main(num_threads=1):
    feasible = itertools.product(characters, repeat=length)
    total = len(characters) ** length
    result = None
    if num_threads == 1:
        pbar = tqdm(
            feasible, ncols=100, total=total, desc="Cracking..."
        )
        for password, state in pbar:
            if state:
                result = password
                break
            pbar.set_postfix_str(f"cur@{password}")
        pbar.close()
        return result


    with Pool(NUM_THREADS) as pool:
        pbar = tqdm(
            pool.imap(unzip, feasible), 
            ncols=100, total=total, desc="Cracking..."
        )
        for password, state in pbar:
            if state:
                result = password
                break
            pbar.set_postfix_str(f"cur@{password}")

        pbar.close()

    return result


if __name__ == "__main__":
    password = main(8)
    print(password)