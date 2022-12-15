import os
from fs import open_fs
import gnupg

gpg = gnupg.GPG(gnupghome="/home/srvps0tibco20@hs.maricopa.gov/.gnupg")
home_fs = open_fs(".")

files_dir = []
files_dir_clean = []

if os.path.exists("decrypted/"):
    print("Decrypted directory already exists")
else:
    home_fs.makedir(u"decrypted/")
    print("Created decrypted directory")

files = [f for f in os.listdir(".") if os.path.isfile(f)]
for f in files:
    files_dir.append(f)

for x in files_dir:
    length = len(x)
    endLoc = length - 4
    clean_file = x[0:endLoc]
    files_dir_clean.append(clean_file)

for x in files_dir:
    with open(x, "rb") as f:
        status = gpg.decrypt_file(f, passphrase="Deployment$20",output=files_dir_clean[files_dir.index(x)])
        print("ok: ", status.ok)
        print("status: ", status.status)
        print("stderr: ", status.stderr)
        os.rename(files_dir_clean[files_dir.index(x)], "decrypted/" + files_dir_clean[files_dir.index(x)])