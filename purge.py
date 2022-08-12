import datetime
import sys
from ftplib import FTP

from dateutil import parser

file_infos = []


def collect_files(dir_line):
    file_info = {}
    tokens = dir_line.split()
    file_info['size'] = int(tokens[4])
    file_info['ftp_date'] = tokens[5] + " " + tokens[6] + " " + tokens[7]
    file_info['file_name'] = tokens[8]
    ftp_date = parser.parse(file_info['ftp_date'])
    file_info['sortable_date'] = ftp_date.strftime("%Y-%m-%d %H:%M")

    n = datetime.datetime.now()
    delta = n - ftp_date
    file_info['days'] = delta.days

    if file_info['file_name'] == "." or file_info['file_name'] == "..":
        return

    file_infos.append(file_info)


def ftp_date_key(file_info):
    return file_info['sortable_date']


user = sys.argv[1]
pwd = sys.argv[2]
server = sys.argv[3]
folder = sys.argv[4]

# c = number of files to keep, s = megabytes to keep, d = days to keep
trigger_type = sys.argv[5]
trigger_value = int(sys.argv[6])

print("Server: " + server)

ftp = FTP(server)
ftp.login(user, pwd)
ftp.cwd(folder)  # change into "debian" directory
ftp.retrlines('LIST', collect_files)  # list directory contents

file_infos.sort(key=ftp_date_key, reverse=True)

count = 0
acc_size = 0
last_date = ''

for fi in file_infos:
    count = count + 1
    acc_size = acc_size + fi['size']
    trigger_size = acc_size / (1024 * 1024)

    if trigger_type == "c" and count > trigger_value and fi['sortable_date'] != last_date:
        print("Would delete due to count")

    if trigger_type == "s" and trigger_size > trigger_value and fi['sortable_date'] != last_date:
        print("Would delete due to size")

    if trigger_type == "d" and fi['days'] > trigger_value:
        print("Would delete due to date")

    last_date = fi['sortable_date']
    print(fi['sortable_date'] + " " + fi['file_name'] + " " + str(fi['days']) + " " + str(trigger_size) + " " + str(
        count))

ftp.quit()
