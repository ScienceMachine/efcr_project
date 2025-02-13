""" 
compute per-agency and per-regulation features and write to a postgres db
"""

import json
import logging
import os
from dataclasses import asdict
from typing import Optional, List

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    DeclarativeBase,
    Session,
)
from sqlalchemy.engine import Engine
import sqlalchemy

from backend.ecfr_api_utils import get_agencies, get_regulation, Agency, Regulation
from backend.feature_extraction import AgencyFeatures, RegulationFeatures

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
    short_name: Mapped[Optional[str]]
    word_count: Mapped[int]


class ProcessingDeadLetter(Base):
    """Log some info about failed computations"""

    __tablename__ = "dead_letter"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[str]
    agency_name: Mapped[str]
    references: Mapped[str]
    exception_msg: Mapped[str]


def get_engine() -> Engine:
    connection_str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    return create_engine(connection_str)


def get_all_ds(min_year: int) -> List[str]:
    """
    currently just gets dates quartely since some min date
    (eCFR has data going back to 2017)
    """
    # TODO: update to stop generating dates after current date
    result = []
    for year in range(min_year, 2026):
        for month in ["02", "05", "08", "11"]:
            result.append(f"{year}-{month}-01")
    return result
