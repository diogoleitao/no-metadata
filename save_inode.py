#   Receives two File objects, the first one relative to the inode we want to save (opened in binary mode),
#   and the second one relative to the file we want to save it to (opened in binary, append mode).
def save_inode(disk_file, output_file):
    position = disk_file.tell()
    inode = disk_file.read(128)

    position_length = len(str(position))
    for (int i = 0; i < 16 - position_length; i++):
        output_file.write('0')

    output_file.write(position)
    output_file.write(inode)

#   Receives two file objects, the first relative to the disk we want to recover from (opened in binary mode),
#   and the second relative to the file with the retrieve information (also opened in binary mode).
def read_inodes(disk_file, input_file):

    while(len(position_string = input_file.read(16)) > 0):
        position = int(position_string)
        inode = input_file.read(128)

        disk_file.seek(position)
        disk_file.write(inode)
