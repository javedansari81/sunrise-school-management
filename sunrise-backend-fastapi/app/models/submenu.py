from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class SubMenu(Base):
    __tablename__ = "submenus"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    menu_class = Column(String(100), nullable=False)
    order_by = Column(Integer, nullable=False, default=1)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    menu = relationship("Menu", back_populates="submenus")
    user = relationship("User", back_populates="submenus")
