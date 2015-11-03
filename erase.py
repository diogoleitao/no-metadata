import binascii


def hexConverter(byte):
    reversed_hex_str = "0x"
    i = 0
    while i < len(byte):
        reversed_hex_str += byte[len(byte) - 2 - i]
        reversed_hex_str += byte[len(byte) - 1 - i]
        i += 2
    return int(reversed_hex_str, 0)


def getDevSize():
    gbytes = raw_image.tell() / (1024 ** 3)
    print gbytes

if __name__ == "__main__":

    # CONSTANTS
    SUPERBLOCK = 1024
    ROOT_INODE_NO = 2
    INODE_SIZE = 128
    DIR_MASK = 16384  # Mask for bit-by-bit check if inode is directory (0x4000)

    # STRUCTS
    sb_offsets = {
        "block_size": 24,
        "blocks_per_group": 32,
        "inodes_per_group": 40
        # "inode_count": 4,
        # "block_count": 4,
    }

    bgdt_offsets = {
        "inode_bitmap": 4,
        "bg_inode_table": 8
    }

    inode_offsets = {
        "inode_mode": 0,
        "inode_first_data_block": 40
    }

    sb_values = {
        "block_size": 0,
        "blocks_per_group": 0,
        "inodes_per_group": 0
        # "inode_count": 0,
        # "block_count": 0,
    }

    bgdt_values = {
        "inode_bitmap": 0,
        "bg_inode_table": 0
    }

    inode_values = {
        "inode_mode": 0,
        "inode_first_data_block": 0
    }

    # VARIABLES
    dir_full_path = "/dev/sdb1"
    block_group_descriptor_table = 0
    first_inode_table = 0 * sb_values["block_size"]
    # second_inode_table = 33710 * info_values["block_size"]

    with open(dir_full_path, "r") as raw_image:
        for field, offset in sb_offsets.iteritems():
            raw_image.seek(SUPERBLOCK + offset)
            sb_values[field] = hexConverter(binascii.b2a_hex(raw_image.read(4)))

        sb_values["block_size"] = 1024 << sb_values["block_size"]

        if sb_values["block_size"] > 1024:
            block_group_descriptor_table = sb_values["block_size"]
        else:
            block_group_descriptor_table = sb_values["block_size"] * 2

        for field, offset in bgdt_offsets.iteritems():
            raw_image.seek(block_group_descriptor_table + offset)
            bgdt_values[field] = hexConverter(binascii.b2a_hex(raw_image.read(4)))

        root_inode = bgdt_values["bg_inode_table"] * sb_values["block_size"] + INODE_SIZE * ROOT_INODE_NO

        raw_image.seek(root_inode + inode_offsets["inode_mode"])
        inode_values["inode_mode"] = binascii.b2a_hex(raw_image.read(2))

        raw_image.seek(root_inode + inode_offsets["inode_first_data_block"])
        inode_values["inode_first_data_block"] = hexConverter(binascii.b2a_hex(raw_image.read(4)))

        raw_image.seek(inode_values["inode_first_data_block"] * sb_values["block_size"])
        while True:
            print binascii.b2a_qp(raw_image.read(4)),
            # print raw_image.tell(),
            raw_input()
