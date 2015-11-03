import binascii


def hexConverter(byte):
    reversed_hex = 0
    reversed_hex_str = ""
    i = 0
    # probably wrong
    while i < byte.length:
        reversed_hex_str += byte[byte.length - 2 - i]
        reversed_hex_str += byte[byte.length - 1 - i]
        i += 2
    # convert to dec part missing
    return reversed_hex

if __name__ == "__main__":
    """dir_full_path = raw_input("Please enter the
        full path for the directory to
        have its metadata erased: ")"""

    info_bytes = {
        "inode_count": 4,
        "block_count": 4,
        "block_size": 4,
        "blocks_per_group": 4,
        "inodes_per_group": 4
    }

    info_values = {
        "inode_count": 0,
        "block_count": 0,
        "block_size": 0,
        "blocks_per_group": 0,
        "inodes_per_group": 0
    }

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
