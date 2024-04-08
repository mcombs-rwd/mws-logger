from typing import Optional
from sqlalchemy.orm import (Mapped, mapped_column, declarative_base)

from datetime import datetime

Base = declarative_base()


class Water_reading(Base):
    """Recorded measurements from water meters and rain gauges"""
    __tablename__ = "water_reading"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    date: Mapped[datetime]
    sensor_id: Mapped[str]
    value: Mapped[int]

    def __repr__(self) -> str:
        return f"<Water_reading(id={self.id}, date={self.date}, sensor={self.sensor_id}, value={self.value})>"


class Sensor(Base):
    """Water flowmeters and rain gauges

    Water flow meters report total gallons, they are cumulative.
    Rain gauges report current inches
    """
    __tablename__ = "sensor"
    id: Mapped[str] = mapped_column(primary_key=True, unique=True)
    name: Mapped[Optional[str]]
    cumulative: Mapped[bool]
    units: Mapped[str]

    def __repr__(self) -> str:
        return f"<Sensor(id={self.id}, name={self.name}, cumulative={self.cumulative})>"
