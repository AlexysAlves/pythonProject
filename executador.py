import time
for i in range(100):
    exec(open("./main.py").read())
    time.sleep(5)
