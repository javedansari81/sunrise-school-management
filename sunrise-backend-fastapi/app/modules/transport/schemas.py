"""Request and response models of the transport operations module."""
from datetime import date, time
from decimal import Decimal
from typing import List, Optional

from typing_extensions import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.fees.schemas import MoneyIn
from app.modules.transport.constants import RateBasis

Money = Decimal
KmIn = Annotated[Decimal, Field(ge=0, max_digits=6, decimal_places=2)]


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Transport types
# ---------------------------------------------------------------------------

class TransportTypeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: Optional[str] = None
    capacity: Optional[int] = Field(default=None, gt=0)
    sort_order: int = 0
    is_active: bool = True


class TransportTypeUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = None
    capacity: Optional[int] = Field(default=None, gt=0)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class TransportTypeOut(ORM):
    id: int
    name: str
    description: Optional[str]
    capacity: Optional[int]
    sort_order: int
    is_active: bool


# ---------------------------------------------------------------------------
# Vehicles
# ---------------------------------------------------------------------------

class VehicleCreate(BaseModel):
    transport_type_id: int
    registration_number: str = Field(min_length=1, max_length=30)
    capacity: Optional[int] = Field(default=None, gt=0)
    driver_name: Optional[str] = Field(default=None, max_length=100)
    driver_phone: Optional[str] = Field(default=None, max_length=20)
    remarks: Optional[str] = None
    is_active: bool = True


class VehicleUpdate(BaseModel):
    transport_type_id: Optional[int] = None
    registration_number: Optional[str] = Field(default=None, min_length=1, max_length=30)
    capacity: Optional[int] = Field(default=None, gt=0)
    driver_name: Optional[str] = Field(default=None, max_length=100)
    driver_phone: Optional[str] = Field(default=None, max_length=20)
    remarks: Optional[str] = None
    is_active: Optional[bool] = None


class VehicleOut(ORM):
    id: int
    transport_type_id: int
    registration_number: str
    capacity: Optional[int]
    driver_name: Optional[str]
    driver_phone: Optional[str]
    remarks: Optional[str]
    is_active: bool


# ---------------------------------------------------------------------------
# Routes and stops
# ---------------------------------------------------------------------------

class StopCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    sequence: Optional[int] = Field(default=None, gt=0, description="Leave out to add the stop at the end")
    distance_km: Optional[KmIn] = None
    pickup_time: Optional[time] = None
    drop_time: Optional[time] = None
    is_active: bool = True


class StopUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    distance_km: Optional[KmIn] = None
    pickup_time: Optional[time] = None
    drop_time: Optional[time] = None
    is_active: Optional[bool] = None


class StopOrder(BaseModel):
    stop_ids: List[int] = Field(min_length=1, description="Every stop of the route, in riding order")


class StopOut(ORM):
    id: int
    route_id: int
    name: str
    sequence: int
    distance_km: Optional[Decimal]
    pickup_time: Optional[time]
    drop_time: Optional[time]
    is_active: bool


class RouteCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    vehicle_id: Optional[int] = None
    is_active: bool = True
    stops: List[StopCreate] = Field(default_factory=list, description="Stops in riding order")


class RouteUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    vehicle_id: Optional[int] = None
    is_active: Optional[bool] = None


class RouteOut(ORM):
    id: int
    name: str
    description: Optional[str]
    vehicle_id: Optional[int]
    is_active: bool
    stops: List[StopOut]


# ---------------------------------------------------------------------------
# Rates
# ---------------------------------------------------------------------------

class RateCreate(BaseModel):
    session_year_id: int
    basis: RateBasis
    transport_type_id: Optional[int] = None
    route_stop_id: Optional[int] = None
    distance_from_km: Optional[KmIn] = None
    distance_to_km: Optional[KmIn] = None
    monthly_amount: MoneyIn
    description: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = True

    @model_validator(mode="after")
    def _shape(self):
        if self.basis == RateBasis.PER_STOP:
            if self.route_stop_id is None:
                raise ValueError("PER_STOP rates need route_stop_id")
            if self.distance_from_km is not None or self.distance_to_km is not None:
                raise ValueError("PER_STOP rates take no distances")
        elif self.basis == RateBasis.DISTANCE_SLAB:
            if self.route_stop_id is not None:
                raise ValueError("DISTANCE_SLAB rates take no route_stop_id")
            if self.distance_from_km is None or self.distance_to_km is None:
                raise ValueError("DISTANCE_SLAB rates need distance_from_km and distance_to_km")
            if self.distance_to_km <= self.distance_from_km:
                raise ValueError("distance_to_km must be more than distance_from_km")
        else:
            if self.transport_type_id is None:
                raise ValueError("FLAT rates need transport_type_id")
            if self.route_stop_id is not None or self.distance_from_km is not None or self.distance_to_km is not None:
                raise ValueError("FLAT rates take no route_stop_id or distances")
        return self


class RateUpdate(BaseModel):
    distance_from_km: Optional[KmIn] = None
    distance_to_km: Optional[KmIn] = None
    monthly_amount: Optional[MoneyIn] = None
    description: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None


class RateOut(ORM):
    id: int
    session_year_id: int
    basis: str
    transport_type_id: Optional[int]
    route_stop_id: Optional[int]
    distance_from_km: Optional[Decimal]
    distance_to_km: Optional[Decimal]
    monthly_amount: Money
    description: Optional[str]
    is_active: bool


class RateCopy(BaseModel):
    from_session_year_id: int
    to_session_year_id: int


class RateCopyResult(BaseModel):
    copied: int


class Placement(BaseModel):
    """Where a student rides. Route, stop and vehicle type are checked against each other."""
    transport_type_id: Optional[int] = Field(default=None, description="Defaults to the route vehicle's type")
    route_id: Optional[int] = Field(default=None, description="Defaults to the stop's route")
    route_stop_id: Optional[int] = None
    distance_km: Optional[KmIn] = Field(default=None, description="Defaults to the stop's distance")


class RateQuote(Placement):
    session_year_id: int


class RateQuoteOut(BaseModel):
    transport_type_id: int
    route_id: Optional[int]
    route_stop_id: Optional[int]
    distance_km: Optional[Decimal]
    transport_rate_id: Optional[int]
    basis: Optional[str]
    monthly_amount: Optional[Money]


# ---------------------------------------------------------------------------
# Assignments
# ---------------------------------------------------------------------------

class AssignmentCreate(Placement):
    student_id: int
    session_year_id: int
    start_date: date
    pickup_location: Optional[str] = Field(default=None, max_length=200)
    drop_location: Optional[str] = Field(default=None, max_length=200)
    monthly_amount: Optional[MoneyIn] = Field(default=None, description="Set to override the rate")
    remarks: Optional[str] = None
    allow_over_capacity: bool = False


class AssignmentChange(Placement):
    """
    Change route, stop, vehicle type or amount from `effective_date` (the first
    day on the new terms). Fields left out keep their current value; a field
    sent as null is cleared. Without monthly_amount the rate is looked up again.
    """
    effective_date: date
    pickup_location: Optional[str] = Field(default=None, max_length=200)
    drop_location: Optional[str] = Field(default=None, max_length=200)
    monthly_amount: Optional[MoneyIn] = None
    remarks: Optional[str] = None
    reason: Optional[str] = None
    allow_over_capacity: bool = False


class AssignmentDiscontinue(BaseModel):
    end_date: date = Field(description="Last day of riding")
    reason: Optional[str] = None


class AssignmentCancel(BaseModel):
    reason: str = Field(min_length=1)


class PauseCreate(BaseModel):
    from_period: date = Field(description="First paused month (any day of it)")
    to_period: date = Field(description="Last paused month (any day of it)")
    reason: Optional[str] = None

    @model_validator(mode="after")
    def _order(self):
        if (self.to_period.year, self.to_period.month) < (self.from_period.year, self.from_period.month):
            raise ValueError("to_period must not be before from_period")
        return self


class PauseOut(ORM):
    id: int
    assignment_id: int
    from_period: date
    to_period: date
    reason: Optional[str]
    is_active: bool


class BillingSummary(BaseModel):
    """What the fee module bills for an assignment."""
    billed_from: Optional[date]
    billed_to: Optional[date]
    billed_months: List[date]


class AssignmentOut(ORM):
    id: int
    student_id: int
    session_year_id: int
    transport_type_id: int
    route_id: Optional[int]
    route_stop_id: Optional[int]
    distance_km: Optional[Decimal]
    pickup_location: Optional[str]
    drop_location: Optional[str]
    start_date: date
    end_date: Optional[date]
    monthly_amount: Money
    transport_rate_id: Optional[int]
    amount_overridden: bool
    previous_assignment_id: Optional[int]
    is_active: bool
    end_reason: Optional[str]
    remarks: Optional[str]
    pauses: List[PauseOut]
    # Filled in by the service
    student_name: Optional[str] = None
    admission_number: Optional[str] = None
    billing: Optional[BillingSummary] = None


class AssignmentResult(BaseModel):
    """An assign, change, discontinue, cancel or pause: the assignment(s) and what billing did."""
    assignment: AssignmentOut
    previous: Optional[AssignmentOut] = None
    plan_lines: dict
    dues: Optional[dict] = None
    warnings: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Rosters
# ---------------------------------------------------------------------------

class Rider(BaseModel):
    assignment_id: int
    student_id: int
    student_name: str
    admission_number: str
    class_name: Optional[str]
    transport_type_id: int
    pickup_location: Optional[str]
    drop_location: Optional[str]
    paused: bool


class RosterStop(BaseModel):
    stop: Optional[StopOut]
    riders: List[Rider]


class RouteRoster(BaseModel):
    route_id: int
    route_name: str
    vehicle: Optional[VehicleOut]
    seats: Optional[int]
    on_date: date
    riding: int
    paused: int
    over_capacity: bool
    stops: List[RosterStop]


class VehicleRoster(BaseModel):
    vehicle: VehicleOut
    seats: Optional[int]
    on_date: date
    riding: int
    over_capacity: bool
    routes: List[RouteRoster]
