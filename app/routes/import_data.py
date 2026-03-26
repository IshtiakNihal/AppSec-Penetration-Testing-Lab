from flask import Blueprint, jsonify, request
from lxml import etree

import_bp = Blueprint("import", __name__, url_prefix="/api")


@import_bp.route("/import", methods=["POST"])
def import_data():
    xml_data = request.data
    try:
        parser = etree.XMLParser(resolve_entities=True, load_dtd=True)
        root = etree.fromstring(xml_data, parser)
        return jsonify({"status": "ok", "data": etree.tostring(root).decode()})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
