import enum
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class PenaltyType(enum.StrEnum):
    NONE = "none"
    PLUS_TWO = "+2"
    DNF = "dnf"


class Solve(Base):
    __tablename__ = "solves"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    raw_time_ms = Column(Integer, nullable=False)  # Time in milliseconds (e.g. 12340 = 12.34s)
    penalty = Column(
        String(10), default=PenaltyType.NONE.value, nullable=False
    )  # 'none', '+2', 'dnf'
    scramble = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="solves")

    @property
    def final_time_ms(self) -> int | None:
        """Returns final time in ms taking into account penalties, or None if DNF."""
        if self.penalty == PenaltyType.DNF.value:
            return None
        if self.penalty == PenaltyType.PLUS_TWO.value:
            return self.raw_time_ms + 2000
        return self.raw_time_ms
