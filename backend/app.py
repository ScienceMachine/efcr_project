from typing import Dict

from flask import Flask

from .ecfr_api_utils import (
    get_agencies,
    CfrReference,
    Agency,
)
from .feature_extraction import get_agency_features

app = Flask(__name__)


@app.route("/")
def get_summary():
    """Get summary of regulation stats by agency across agencies"""
    all_agencies = get_agencies()
    result_str = "\n".join(x.name for x in all_agencies)
    return f"<p>{result_str}</p>"


@app.route("/agency_details")
def get_agency_details():
    """Get payload w/ full stats, incl. historical"""
    refs = CfrReference.from_json([{"title": 36, "chapter": "VIII"}])
    agency = Agency(name="Ramjamz", short_name="jamz", cfr_references=refs)
    agency_features = get_agency_features(agency=agency, date="2025-01-01")
    result_str = str(agency_features.word_count)
    return f"<p>{result_str}</p>"
