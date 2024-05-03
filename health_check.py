import os
from datetime import datetime as dt
from subprocess import PIPE, Popen

import pytz
import requests


def ping_server(url: str, service_name: str):
    IST = pytz.timezone("Asia/Kolkata")
    # curr_time = dt.now(IST)

    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise
        print(f"[{dt.now(IST)}] {service_name} working fine!")
    except Exception:
        print(f"[{dt.now(IST)}] {service_name} not reachable, restarting container!!")
        commands = [
            ["docker", "compose", "stop", f"{service_name}"],
            ["docker", "compose", "up", "-d", "--no-deps", f"{service_name}"],
        ]
        for c in commands:
            p = Popen(c, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate()
            print(output.decode("utf-8"))
            print(err.decode("utf-8"))
            rc = p.returncode
            if rc != 0:
                print(
                    f"[{dt.now(IST)}] Error with restarting {service_name}!! Please check!"
                )


if __name__ == "__main__":
    os.environ["HOST_IP"] = ""
    HOST_IP = os.environ.get("HOST_IP", "")
    ping_server(f"http://{HOST_IP}:8000/", "backend")
    ping_server(f"http://{HOST_IP}:8080/", "front_end")
