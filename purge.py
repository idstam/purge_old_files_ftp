dir_lines = []

from ftplib import FTP

ftp = FTP('ftp.us.debian.org')  # connect to host, default port
ftp.login()  # user anonymous, passwd anonymous@
ftp.cwd('debian')  # change into "debian" directory
ftp.retrlines('LIST', )  # list directory contents

ftp.quit()


def collect_files(dir_line):
    dir_lines.append(dir_line)
