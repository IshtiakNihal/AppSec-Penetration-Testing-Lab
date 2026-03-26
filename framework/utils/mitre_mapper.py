MAPPINGS = {
    "sqli": "T1190",
    "xss": "T1059",
    "ssrf": "T1190",
    "xxe": "T1190",
    "idor": "T1068",
    "file_upload": "T1105",
}


def map_to_mitre(vuln_id: str) -> str:
    return MAPPINGS.get(vuln_id, "T0000")
