from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)

    # Relationships
    users = relationship("User", back_populates="department")
    courses = relationship("Course", back_populates="department")
