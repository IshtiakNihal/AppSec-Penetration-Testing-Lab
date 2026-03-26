import json

import yaml

from framework.reporting.report_generator import generate_report


def run(output_dir: str):
    vulnerabilities_path = f"{output_dir}/vulnerabilities.json"
    with open(vulnerabilities_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    generate_report(data, f"{output_dir}/pentest_report.pdf", f"{output_dir}/summary.html")


if __name__ == "__main__":
    with open("framework/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    run(config["output_dir"])
