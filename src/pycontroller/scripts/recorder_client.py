from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H:%M:%S:%MS")
print("Current Time =", current_time)

import time

def current_milli_time():
    return round(time.time() * 1000)

print(current_milli_time())