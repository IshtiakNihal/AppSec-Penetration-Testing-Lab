import json
import sys

import yaml

from framework.utils.logger import setup_logger
from framework.utils.request_wrapper import RequestWrapper

logger = setup_logger("recon")


def run(target: str, output_path: str, timeout: int = 10):
    client = RequestWrapper(target, timeout=timeout)
    findings = {
        "target": target,
        "endpoints": ["/", "/login", "/search", "/upload", "/admin"],
        "server": None,
    }

    try:
        response = client.get("/")
        findings["server"] = response.headers.get("Server", "unknown")
    except Exception as exc:
        logger.error("Recon failed: %s", exc)

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(findings, handle, indent=2)

    logger.info("Recon complete: %s", output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python _01_reconnaissance.py <target>")
        sys.exit(1)

    with open("framework/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    run(sys.argv[1], f"{config['output_dir']}/reconnaissance.json")
