import argparse
import datetime
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


arg_parser = argparse.ArgumentParser(description='Delete old files from FTP folder.')
arg_parser.add_argument('--user', type=str, help='Username')
arg_parser.add_argument('--password', type=str, help='Password')
arg_parser.add_argument('--hostname', type=str, help='Hostname')
arg_parser.add_argument('--folder', type=str, default='/', help='Folder')
arg_parser.add_argument('--count', type=int, default='1000', help='Number of files to keep')
arg_parser.add_argument('--size', type=int, default='1000', help='Total size in MB to keep')
arg_parser.add_argument('--days', type=int, default='100', help='Number of days to keep')
arg_parser.add_argument('--verbose', type=bool, default=False, help='Output trace log')
arg_parser.add_argument('--dryrun', type=bool, default=False, help='Do not do the actual delete. Just log it')
args = arg_parser.parse_args()

if args.verbose:
    print("Server: " + args.hostname)
    print("User: " + args.user)
    print("Folder: " + args.folder)
    print("Number of files: " + str(args.count))
    print("Total size in MB: " + str(args.size))
    print("Number of days: " + str(args.days))


ftp = FTP(args.hostname)
ftp.login(args.user, args.password)
ftp.cwd(args.folder)  # change into "debian" directory
ftp.retrlines('LIST', collect_files)  # list directory contents

file_infos.sort(key=ftp_date_key, reverse=True)

count = 0
acc_size = 0
last_date = ''

do_delete = False
reason = ''


for fi in file_infos:
    if args.verbose and count % 25 == 0:
        print("\naction " + '\t' + 'count' + "\t" + 'size' + "\t" + 'days' + '\t' + 'file name' + '\t\t' + reason)

    count = count + 1
    acc_size = acc_size + fi['size']
    trigger_size = acc_size / (1024 * 1024)

    if count > args.count and fi['sortable_date'] != last_date and do_delete is False:
        do_delete = True
        if args.verbose:
            reason = "Count exceeded " + str(args.count)
            print("\naction " + '\t' + 'count' + "\t" + 'size' + "\t" + 'days' + '\t' + 'file name' + '\t\t' + reason)

    if trigger_size > args.size and fi['sortable_date'] != last_date and do_delete is False:
        do_delete = True
        if args.verbose:
            reason = "Size exceeded " + str(args.size)
            print("\naction " + '\t' + 'count' + "\t" + 'size' + "\t" + 'days' + '\t' + 'file name' + '\t\t' + reason)

    if fi['days'] > args.days and do_delete is False:
        do_delete = True
        if args.verbose:
            reason = "Days exceeded " + str(args.days)
            print("\naction " + '\t' + 'count' + "\t" + 'size' + "\t" + 'days' + '\t' + 'file name' + '\t\t' + reason)

    last_date = fi['sortable_date']

    if do_delete:
        if args.verbose:

            if not args.dryrun:
                print("Delete" + '\t' + str(count) + "\t" + str(int(trigger_size)) + "\t" + str(fi['days']) + '\t' + fi[
                    'file_name'])
                ftp.delete(args.folder + fi['file_name'])
            else:
                print("Deletable" + '\t' + str(count) + "\t" + str(int(trigger_size)) + "\t" + str(fi['days']) + '\t' +
                      fi[
                          'file_name'])
    else:
        if args.verbose:
            print("Keep" + '\t' + str(count) + "\t" + str(int(trigger_size)) + "\t" + str(fi['days']) + '\t' + fi['file_name'])

ftp.quit()
