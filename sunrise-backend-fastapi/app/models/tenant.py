"""
Tenant mixin.

Every model whose table carries a ``school_id`` column inherits from
``TenantMixin``. Session events in ``app.core.tenant`` then:

* add ``WHERE school_id = <current school>`` to every ORM query that touches
  a tenant model, including joins and relationship loads, and
* stamp ``school_id`` on new rows and refuse writes into another school.

Routes and CRUD code therefore never filter by school by hand.
"""
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import declared_attr


class TenantMixin:
    @declared_attr
    def school_id(cls):
        return Column(Integer, ForeignKey("schools.id"), nullable=False, index=True)
