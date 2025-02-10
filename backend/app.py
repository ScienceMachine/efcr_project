from typing import Dict

from flask import Flask


app = Flask(__name__)


@app.route("get_summary")
def get_summary():
    """Get summary of regulation stats by agency across agencies"""
    raise NotImplementedError


@app.route("agency_details")
def get_agency_details(agency: str) -> Dict[str, str]:
    """Get payload w/ full stats, incl. historical"""
    raise NotImplementedError
