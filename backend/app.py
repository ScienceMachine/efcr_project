from typing import Dict
import random

from flask import Flask, jsonify, Response

from .ecfr_api_utils import (
    get_agencies,
    CfrReference,
    Agency,
)
from .feature_extraction import get_agency_features

app = Flask(__name__)


@app.route("/summary")
def get_summary() -> Response:
    """Get summary of regulation stats by agency across agencies"""
    all_agencies = get_agencies()
    results = []
    for i, agency in enumerate(all_agencies):
        results.append(
            {
                "result_id": i,
                "name": agency.name,
                "short_name": agency.short_name,
                "new_word_count": random.randint(0, 10_000_000),
                "old_word_count": random.randint(0, 10_000_000),
            }
        )
    print(f"Returning {len(results)} results...")
    response = jsonify(results)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/agency_details")
def get_agency_details():
    """Get payload w/ full stats, incl. historical"""
    refs = CfrReference.from_json([{"title": 36, "chapter": "VIII"}])
    agency = Agency(name="Ramjamz", short_name="jamz", cfr_references=refs)
    agency_features = get_agency_features(agency=agency, date="2025-01-01")
    result_str = str(agency_features.word_count)
    return f"<p>{result_str}</p>"
