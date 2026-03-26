import json
import sys

import yaml

from framework.utils.logger import setup_logger
from framework.utils.request_wrapper import RequestWrapper

logger = setup_logger("scan")


def run(target: str, output_path: str, timeout: int = 10):
    client = RequestWrapper(target, timeout=timeout)
    findings = []

    try:
        response = client.get("/search?q=<script>alert(1)</script>")
        if "<script>alert(1)</script>" in response.text:
            findings.append({"id": "reflected_xss", "severity": "high"})
    except Exception:
        pass

    try:
        response = client.get("/download?file=../../../../etc/passwd")
        if "root:" in response.text:
            findings.append({"id": "path_traversal", "severity": "high"})
    except Exception:
        pass

    data = {"target": target, "findings": findings}
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)

    logger.info("Scanning complete: %s", output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python _03_scanning.py <target>")
        sys.exit(1)

    with open("framework/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    run(sys.argv[1], f"{config['output_dir']}/vulnerabilities.json")
