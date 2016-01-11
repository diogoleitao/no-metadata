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


# Receives two file objects, the first one is the inode we want to save (opened in binary mode),
# and the second one is to the file we want to save it to (opened in binary, append mode).
def hide_inodes(disk_file_path, output_file_path, index):
    with open(disk_file_path, "r+b") as disk_file:
        disk_file.seek(index)
        position = disk_file.tell()
        inode = disk_file.read(128)

        with open(output_file_path, "wba") as output_file:
            position_length = len(str(position))
            i = 0
            while i < 16 - position_length:
                output_file.write('0')
                i += 1

            output_file.write(str(position))
            output_file.write(inode)

        disk_file.seek(index)
        i = 0
        while i < 128:
            disk_file.write('0')
            i += 1


# Receives two file objects, the first relative to the disk we want to recover from (opened in binary mode),
# and the second relative to the file with the retrieve information (also opened in binary mode).
def recover_inodes(disk_file_path, input_file_path):
    with open(disk_file_path, "r+b") as disk_file:
        with open(input_file_path, "rb") as input_file:
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

    # STRUCTS
    sb_offsets = {
        "block_size": 24,
        "blocks_per_group": 32,
        "inodes_per_group": 40
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
    block_group_descriptor_table = 0

    device = "/dev/" + raw_input("> Please enter the device name from the /dev directory (e.g., sda1):\n")
    operation = raw_input("> Please choose if you want to [r]ecover or [h]ide:\n")
    backup_file = raw_input("> Please enter the absolute path for the backup file:\n")

    if operation == "r":
        recover_inodes(device, backup_file)
    elif operation == "h":
        while True:
            directory = raw_input("> Please enter the absolute path for the directory that contains the files to be hidden. To terminate the program, type \"exit\".\n").strip()
            if directory.lower() == "exit":
                quit()
            else:
                full_path = directory.split("/")
                if "" in full_path:
                    full_path.remove("")
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

                    cur_dir = 0
                    # Find the directory iteratively
                    while cur_dir < len(full_path):
                        inode_no = hexConverter(binascii.b2a_hex(raw_image.read(4)))
                        record_length = hexConverter(binascii.b2a_hex(raw_image.read(2)))
                        name_length = hexConverter(binascii.b2a_hex(raw_image.read(1)))
                        file_type = hexConverter(binascii.b2a_hex(raw_image.read(1)))
                        inode_name = binascii.b2a_qp(raw_image.read(name_length))
                        padding = raw_image.read(record_length - name_length - 8)

                        """
                        print inode_name,
                        raw_input()
                        """

                        if inode_name == full_path[cur_dir]:
                            cur_dir += 1

                            table_no = (inode_no - 1) / sb_values["inodes_per_group"]
                            real_inode_no = (inode_no - 1) % sb_values["inodes_per_group"]
                            table_offset = table_no * 32 + 8

                            raw_image.seek(block_group_descriptor_table + table_offset)
                            table_entry = hexConverter(binascii.b2a_hex(raw_image.read(4)))

                            dir_inode = table_entry * sb_values["block_size"] + INODE_SIZE * real_inode_no
                            raw_image.seek(dir_inode + inode_offsets["inode_first_data_block"])

                            first_data_block = hexConverter(binascii.b2a_hex(raw_image.read(4)))
                            raw_image.seek(first_data_block * sb_values["block_size"])
                    hide_inodes(device, backup_file, dir_inode)
                    print "Operation successful."
    else:
        print "Wrong command. Exiting..."
        quit()
