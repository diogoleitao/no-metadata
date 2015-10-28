import binascii
import os

if __name__ == "__main__":
    """dir_full_path = raw_input("Please enter the
        full path for the directory to
        have its metadata erased: ")"""

    dir_full_path = "/dev/sda"
    with open(dir_full_path, "r") as raw_image:
        raw_image.seek(0, os.SEEK_END)
        gbytes = raw_image.tell() / (1024 ** 3)
        print gbytes
        while True:
            print binascii.b2a_qp(raw_image.read(4)),
            raw_input()
