import subprocess

while True:
    p = subprocess.Popen(['python' ,'RainbowFarm.py'],shell=True).wait()

    if p != 0:
        try:
            print 'Program restarting >>>>>>>>>>>>>>>>>'
        except Exception as e:
            print e
        continue
    else:
        break
