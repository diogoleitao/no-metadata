import binascii
import os

if __name__ == "__main__":
    """dir_full_path = raw_input("Please enter the
        full path for the directory to
        have its metadata erased: ")"""

    superblock = 1024
    block_group_descriptor_table = 4096
    second_inode_table = 33710 * 4096

    file_to_delete = 942 * 4096 + 3390 * 128

    dir_full_path = "/dev/sdc1"
    with open(dir_full_path, "r") as raw_image:
        raw_image.seek(file_to_delete)  # start of second inode table
        # gbytes = raw_image.tell() / (1024 ** 3)
        # print gbytes
        while True:
            print binascii.b2a_hex(raw_image.read(4)),
            raw_input()
