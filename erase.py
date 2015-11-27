import binascii


# Little endian to human-readable number converter
def hexConverter(byte):
    reversed_hex_str = "0x"
    i = 0
    while i < len(byte):
        reversed_hex_str += byte[len(byte) - 2 - i]
        reversed_hex_str += byte[len(byte) - 1 - i]
        i += 2
    return int(reversed_hex_str, 0)


# Auxiliary function to get the device's size (in GiB)
# Not used
def getDevSize():
    gbytes = raw_image.tell() / (1024 ** 3)
    return gbytes


# Receives two file objects, the first one is the inode we want to save (opened in binary mode),
# and the second one is to the file we want to save it to (opened in binary, append mode).
def save_inode(disk_file, output_file):
    position = disk_file.tell()
    inode = disk_file.read(128)

    position_length = len(str(position))
    i = 0
    while i < 16 - position_length:
        output_file.write('0')
        i += 1

    output_file.write(position)
    output_file.write(inode)


# Receives two file objects, the first relative to the disk we want to recover from (opened in binary mode),
# and the second relative to the file with the retrieve information (also opened in binary mode).
def read_inodes(disk_file, input_file):
    position_string = input_file.read(16)
    while len(position_string) > 0:
        position = int(position_string)
        inode = input_file.read(128)

        disk_file.seek(position)
        disk_file.write(inode)
        position_string = input_file.read()


if __name__ == "__main__":

    # CONSTANTS
    SUPERBLOCK = 1024
    ROOT_INODE_NO = 2
    INODE_SIZE = 128
    DIR_MASK = 16384  # Mask for bit-by-bit check if inode is directory (0x4000)
    BACKUP_FILE = "/some/file/at/some/directory/well/hidden"

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
    device = "/dev/sdb1"
    block_group_descriptor_table = 0
    first_inode_table = 0 * sb_values["block_size"]  # Pointless operation, just to remember us that we need to do the multiplication later
    # second_inode_table = 33710 * info_values["block_size"]  # Not needed (?)

    while True:
        directory = raw_input("Please enter the absolute path for the directory that contains the files to be hidden. To terminate the program, type \"exit\".\n").strip()
        if directory.lower() == "exit":
            quit()
        else:
            with open(device, "r") as raw_image:
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
                    inode_no = hexConverter(binascii.b2a_hex(raw_image.read(4)))
                    record_length = hexConverter(binascii.b2a_hex(raw_image.read(2)))
                    name_length = hexConverter(binascii.b2a_hex(raw_image.read(1)))
                    file_type = hexConverter(binascii.b2a_hex(raw_image.read(1)))
                    inode_name = binascii.b2a_qp(raw_image.read(name_length))
                    padding = record_length - name_length - 8

                    print inode_name,
                    raw_input()  # WAIT FOR CR LF
                save_inode(raw_image, BACKUP_FILE)
