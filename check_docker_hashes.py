# Long pooling for updating containers from remote
# scheduled via crontab on deployed server

import json
from datetime import datetime as dt
from subprocess import PIPE, Popen

images = ["uditmanav/santander_frontend:latest", "uditmanav/santander_backend:latest"]
services = ["front_end", "backend"]


for img, service in zip(images, services):
    # fetch local docker container hash
    cmd1 = ["docker", "images", "--no-trunc", "--quiet", f"{img}"]
    p = Popen(cmd1, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    local_hash, err = p.communicate()
    rc = p.returncode
    local_hash = local_hash.decode("utf-8").strip()
    print(f"{local_hash = }")
    if rc != 0:
        print(f"[{dt.now()}] Error with fetching {service} service's local hash!")
        continue

    # fetch remote docker container hash
    cmd2 = ["docker", "manifest", "inspect", f"{img}"]
    p = Popen(cmd2, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    remote_hash_json, err = p.communicate()
    rc = p.returncode
    rh_dict = json.loads(remote_hash_json.decode("utf-8"))
    remote_hash = rh_dict.get("config").get("digest")
    print(f"{remote_hash = }")
    if rc != 0:
        print(f"[{dt.now()}] Error with fetching {service} service's remote hash!")
        continue

    # compare hash
    if local_hash == remote_hash:
        print(f"[{dt.now()}] Hash matching for {service} service, nothing to do!")
    else:
        print(f"[{dt.now()}] Hash NOT matching for {service} service!!!")
        print("Fetching remote container")
        commands = [
            ["docker", "pull", f"{img}"],
            ["docker", "compose", "stop", f"{service}"],
            ["docker", "compose", "up", "-d", "--no-deps", f"{service}"],
        ]
        for c in commands:
            p = Popen(c, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate()
            print(output)
            print(err)
            rc = p.returncode
            if rc != 0:
                print(f"[{dt.now()}] Error with updating {service}!! Please check!")
