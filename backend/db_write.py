""" 
compute per-agency and per-regulation features and write to a postgres db
"""

import json
import logging
import os
from dataclasses import asdict
from typing import Optional, List, Dict

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    DeclarativeBase,
    Session,
)
from sqlalchemy.engine import Engine
import sqlalchemy

from ecfr_api_utils import get_agencies, get_regulation, Agency, Regulation
from feature_extraction import AgencyFeatures, RegulationFeatures

logger = logging.getLogger(__name__)


POSTGRES_USER: str = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD: str = os.environ["POSTGRES_PASSWORD"]
POSTGRES_HOST: str = os.environ["POSTGRES_HOST"]
POSTGRES_PORT: str = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_DB: str = os.environ["POSTGRES_DB"]

DB_WRITE_BATCH_SIZE: int = 100


def create_db() -> None:
    try:
        connection_str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}"
        engine = create_engine(connection_str, isolation_level="AUTOCOMMIT")
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text(f"CREATE DATABASE {POSTGRES_DB}"))
        logger.info(f"Created DB {POSTGRES_DB}")
    except Exception:
        # too broad, should fix w/ specific exception type and fallback to failure
        logger.info(f"{POSTGRES_DB} already exists, skipping DB creation")


class Base(DeclarativeBase):
    pass


class RegulationOnDate(Base):
    __tablename__ = "regulation_on_date"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[str]
    title: Mapped[str]
    subtitle: Mapped[Optional[str]]
    chapter: Mapped[Optional[str]]
    subchapter: Mapped[Optional[str]]
    part: Mapped[Optional[str]]
    subpart: Mapped[Optional[str]]
    section: Mapped[Optional[str]]
    appendix: Mapped[Optional[str]]
    agency_name: Mapped[Optional[str]]

    word_count: Mapped[int]


class AgencyOnDate(Base):
    __tablename__ = "agency_on_date"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[str]
    name: Mapped[str]
    short_name: Mapped[str]
    word_count: Mapped[int]


class ProcessingDeadLetter(Base):
    """Log some info about failed computations"""

    __tablename__ = "dead_letter"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[str]
    agency_name: Mapped[str]
    references: Mapped[str]
    exception_msg: Mapped[str]


def _get_engine() -> Engine:
    connection_str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    return create_engine(connection_str)


def _create_tables() -> None:
    engine = _get_engine()
    Base.metadata.create_all(engine)


def get_all_ds(min_year: int) -> List[str]:
    """
    currently just gets dates quartely since some min date
    (eCFR has data going back to 2017)
    """
    result = []
    for year in range(min_year, 2026):
        for month in ["02", "05", "08", "11"]:
            result.append(f"{year}-{month}-01")
    return result


def process_api_data() -> None:
    """todo: do batching properly"""
    all_ds = get_all_ds(min_year=2018)
    engine = _get_engine()
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
