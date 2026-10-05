import random
import time
import requests

for i in range(1, 11):
    r = requests.post(
        "http://localhost:8000/users",
        params={"name": f"User{i}", "age": random.randint(18, 65)},
    )
    print(r.status_code, r.json())
    time.sleep(1)