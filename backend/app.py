from flask import Flask, jsonify, Response, request
from flask_cors import CORS
from sqlalchemy import select, alias, func
from sqlalchemy.orm import Session

from backend.db import AgencyOnDate, get_engine

app = Flask(__name__)
CORS(app)


@app.route("/summary")
def get_summary() -> Response:
    """Get summary of regulation stats by agency across agencies"""
    agency_new = alias(AgencyOnDate, "agency_new")
    agency_old = alias(AgencyOnDate, "agency_old")
    query = (
        select(
            agency_new.c.name.label("name"),
            agency_new.c.short_name.label("short_name"),
            func.coalesce(agency_new.c.word_count, 0).label("new_word_count"),
            func.coalesce(agency_old.c.word_count, 0).label("old_word_count"),
        )
        .select_from(agency_new)
        .join(agency_old, agency_new.c.name == agency_old.c.name)
        .where(agency_new.c.date == "2025-02-01")
        .where(agency_old.c.date == "2018-02-01")
        .order_by(agency_new.c.word_count.desc())
    )
    engine = get_engine()
    results = []
    with Session(engine) as session:
        query_result = session.execute(query)
        for i, row in enumerate(query_result):
            results.append(
                {
                    "result_id": i,
                    "name": row.name,
                    "short_name": row.short_name,
                    "new_word_count": row.new_word_count,
                    "old_word_count": row.old_word_count,
                }
            )
    response = jsonify(results)
    # response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/agency_details", methods=["POST"])
def get_agency_details() -> Response:
    """Get payload w/ full stats, incl. historical"""
    agency_name = request.json["agency_name"]
    min_date = request.json.get("min_date", "2018-02-01")
    max_date = request.json.get("max_date", "2025-02-01")

    query = (
        select(AgencyOnDate.date, AgencyOnDate.short_name, AgencyOnDate.word_count)
        .where(AgencyOnDate.name == agency_name)
        .where(AgencyOnDate.date >= min_date)
        .where(AgencyOnDate.date <= max_date)
        .order_by(AgencyOnDate.date)
    )
    engine = get_engine()
    result = {"name": agency_name, "features": []}
    with Session(engine) as session:
        query_result = session.execute(query)
        for row in query_result:
            print(row)
            result["features"].append({"date": row.date, "word_count": row.word_count})
    response = jsonify(result)
    # response.headers.add("Access-Control-Allow-Origin", "*")
    return response
