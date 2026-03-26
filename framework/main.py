import argparse
import yaml

from framework.phases import (
    _01_reconnaissance,
    _02_enumeration,
    _03_scanning,
    _04_exploitation,
    _05_reporting,
)


def main():
    parser = argparse.ArgumentParser(description="Project C Recon Framework")
    parser.add_argument("--target", required=True)
    parser.add_argument("--run-all", action="store_true")
    args = parser.parse_args()

    with open("framework/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    output_dir = config["output_dir"]

    _01_reconnaissance.run(args.target, f"{output_dir}/reconnaissance.json")
    _02_enumeration.run(args.target, f"{output_dir}/enumeration.json")
    _03_scanning.run(args.target, f"{output_dir}/vulnerabilities.json")

    if args.run_all:
        _04_exploitation.run(args.target, f"{output_dir}/exploitation.json")
        _05_reporting.run(output_dir)


if __name__ == "__main__":
    main()
