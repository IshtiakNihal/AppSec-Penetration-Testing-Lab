import json
import sys

import yaml

from framework.utils.logger import setup_logger
from framework.utils.request_wrapper import RequestWrapper

logger = setup_logger("enum")


WORDLIST = ["/api/users", "/api/user/1/statements", "/api/profile", "/download", "/fetch"]


def run(target: str, output_path: str, timeout: int = 10):
    client = RequestWrapper(target, timeout=timeout)
    found = []

    for path in WORDLIST:
        try:
            response = client.get(path)
            if response.status_code < 500:
                found.append({"path": path, "status": response.status_code})
        except Exception:
            continue

    data = {"target": target, "endpoints": found}
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)

    logger.info("Enumeration complete: %s", output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python _02_enumeration.py <target>")
        sys.exit(1)

    with open("framework/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    run(sys.argv[1], f"{config['output_dir']}/enumeration.json")
