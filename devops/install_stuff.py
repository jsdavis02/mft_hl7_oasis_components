import subprocess,sys
print(sys.argv)
subprocess.run('pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org '+str(sys.argv[1]))
