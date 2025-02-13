import json
from typing import List
from dataclasses import asdict

from sqlalchemy.orm import Session

from backend.db import (
    get_engine,
    get_all_ds,
    create_db,
    AgencyOnDate,
    ProcessingDeadLetter,
    RegulationOnDate,
    Base,
)
from backend.feature_extraction import AgencyFeatures, RegulationFeatures
from backend.ecfr_api_utils import get_agencies, get_regulation


def _create_tables() -> None:
    engine = get_engine()
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def process_api_data() -> None:
    """todo: do batching properly"""
    all_ds = get_all_ds(min_year=2018)
    # all_ds = ["2025-02-01", "2018-02-01"]
    engine = get_engine()
    with Session(engine) as session:
        for ds in all_ds:
            agencies_processed = 0
            # logger.info(f"Processing date {ds}...")
            print(f"Processing date {ds}...")
            agencies = get_agencies()
            for agency in agencies:
                try:
                    rows: List[RegulationOnDate | AgencyOnDate] = []
                    regulation_features: List[RegulationFeatures] = []
                    for cfr_reference in agency.cfr_references:
                        regulation = get_regulation(reference=cfr_reference, date=ds)
                        current_reg_features = RegulationFeatures.from_regulation(
                            regulation=regulation
                        )
                        regulation_features.append(current_reg_features)
                        rows.append(
                            RegulationOnDate(
                                date=ds,
                                title=cfr_reference.title,
                                subtitle=cfr_reference.subtitle,
                                chapter=cfr_reference.chapter,
                                subchapter=cfr_reference.subchapter,
                                part=cfr_reference.part,
                                subpart=cfr_reference.subpart,
                                section=cfr_reference.section,
                                appendix=cfr_reference.appendix,
                                word_count=current_reg_features.word_count,
                                agency_name=agency.name,
                            )
                        )

                    agency_features = AgencyFeatures.from_regulation_features(
                        regulation_features=regulation_features
                    )
                    rows.append(
                        AgencyOnDate(
                            date=ds,
                            name=agency.name,
                            short_name=agency.short_name,
                            word_count=agency_features.word_count,
                        )
                    )
                    session.add_all(rows)
                    session.commit()
                except Exception as e:
                    serializable_refs = [asdict(ref) for ref in agency.cfr_references]
                    session.add(
                        ProcessingDeadLetter(
                            date=ds,
                            agency_name=agency.name,
                            references=json.dumps(serializable_refs),
                            exception_msg=str(e),
                        )
                    )
                    session.commit()
                agencies_processed += 1
                if agencies_processed % 10 == 0:
                    print(f"Processed {agencies_processed} agencies...")


if __name__ == "__main__":
    create_db()
    _create_tables()
    process_api_data()
