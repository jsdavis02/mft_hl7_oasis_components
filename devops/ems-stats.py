import subprocess
import sys
print(sys.argv)
out = subprocess.check_output("/opt/tibco/ems/8.4/bin/tibemsadmin -server \"tcp://virps0esb30i02:7222\" -user admin -password oasis -script ems-cmd.txt",shell=True)
with open('/opt/oasis_data/monitoring/queuelist.txt','w') as f:
    f.write(out)
for l in out.splitlines():
    print(l)
