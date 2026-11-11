"""
SQLAlchemy models of the transport operations module. Tables: Database/Tables/T960-T985.

Every model is tenant-scoped (TenantMixin): queries are filtered by the request's
school and new rows are stamped with it by app.core.tenant.
"""
from sqlalchemy import (
    Boolean, Column, Date, DateTime, DECIMAL, ForeignKey, Integer, SmallInteger, String, Text, Time,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.tenant import TenantMixin

Money = DECIMAL(10, 2)
Km = DECIMAL(6, 2)
EAGER = {"eager_defaults": True}


class TransportType(TenantMixin, Base):
    __tablename__ = "transport_types"
    __mapper_args__ = EAGER

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    capacity = Column(Integer)
    sort_order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Vehicle(TenantMixin, Base):
    __tablename__ = "vehicles"
    __mapper_args__ = EAGER

    id = Column(Integer, primary_key=True)
    transport_type_id = Column(Integer, ForeignKey("transport_types.id"), nullable=False)
    registration_number = Column(String(30), nullable=False)
    capacity = Column(Integer)
    driver_name = Column(String(100))
    driver_phone = Column(String(20))
    remarks = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Route(TenantMixin, Base):
    __tablename__ = "routes"
    __mapper_args__ = EAGER

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    stops = relationship(
        "RouteStop", back_populates="route", cascade="all, delete-orphan",
        order_by="RouteStop.sequence", lazy="selectin",
    )


class RouteStop(TenantMixin, Base):
    __tablename__ = "route_stops"
    __mapper_args__ = EAGER

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    sequence = Column(SmallInteger, nullable=False)
    distance_km = Column(Km)
    pickup_time = Column(Time)
    drop_time = Column(Time)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    route = relationship("Route", back_populates="stops")


class TransportRate(TenantMixin, Base):
    __tablename__ = "transport_rates"
    __mapper_args__ = EAGER

    id = Column(Integer, primary_key=True)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)
    basis = Column(String(20), nullable=False)
    transport_type_id = Column(Integer, ForeignKey("transport_types.id"))
    route_stop_id = Column(Integer, ForeignKey("route_stops.id", ondelete="CASCADE"))
    distance_from_km = Column(Km)
    distance_to_km = Column(Km)
    monthly_amount = Column(Money, nullable=False)
    description = Column(String(255))
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TransportAssignment(TenantMixin, Base):
    __tablename__ = "student_transport_assignments"
    __mapper_args__ = EAGER

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)
    transport_type_id = Column(Integer, ForeignKey("transport_types.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"))
    route_stop_id = Column(Integer, ForeignKey("route_stops.id"))
    distance_km = Column(Km)
    pickup_location = Column(String(200))
    drop_location = Column(String(200))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    monthly_amount = Column(Money, nullable=False)
    transport_rate_id = Column(Integer, ForeignKey("transport_rates.id", ondelete="SET NULL"))
    amount_overridden = Column(Boolean, nullable=False, default=False)
    previous_assignment_id = Column(Integer, ForeignKey("student_transport_assignments.id"))
    is_active = Column(Boolean, nullable=False, default=True)
    end_reason = Column(Text)
    remarks = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    ended_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    pauses = relationship(
        "TransportPause", back_populates="assignment", order_by="TransportPause.from_period", lazy="selectin",
    )

    def active_pauses(self):
        return [p for p in self.pauses if p.is_active]


class TransportPause(TenantMixin, Base):
    __tablename__ = "transport_assignment_pauses"
    __mapper_args__ = EAGER

    id = Column(Integer, primary_key=True)
    assignment_id = Column(
        Integer, ForeignKey("student_transport_assignments.id", ondelete="CASCADE"), nullable=False
    )
    from_period = Column(Date, nullable=False)
    to_period = Column(Date, nullable=False)
    reason = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    assignment = relationship("TransportAssignment", back_populates="pauses")
