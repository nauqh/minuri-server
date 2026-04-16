from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from .database import Base


class Suburb(Base):
    __tablename__ = "suburbs"
    __table_args__ = (
        UniqueConstraint("name", "postcode", "state",
                         name="uq_suburbs_name_postcode_state"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False, index=True)
    postcode = Column(String(10), nullable=False, index=True)
    state = Column(String(10), nullable=False, default="VIC")
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    sa4_name = Column(String(120), nullable=True)

    demographics = relationship(
        "SuburbDemographics",
        back_populates="suburb",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Suburb(id={self.id}, name='{self.name}', postcode='{self.postcode}')>"


class GuideArticle(Base):
    __tablename__ = "guide_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False, unique=True, index=True)
    category = Column(String(50), nullable=False, index=True)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    reading_time_min = Column(Integer, nullable=False, default=3)
    is_published = Column(Boolean, nullable=False, default=True)
    is_featured = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<GuideArticle(id={self.id}, slug='{self.slug}', category='{self.category}')>"


class SuburbDemographics(Base):
    __tablename__ = "suburb_demographics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    suburb_id = Column(Integer, ForeignKey("suburbs.id"),
                       nullable=False, unique=True, index=True)
    population_18_25 = Column(Integer, nullable=True)
    total_population = Column(Integer, nullable=True)
    source = Column(String(120), nullable=True)
    updated_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())

    suburb = relationship("Suburb", back_populates="demographics")

    def __repr__(self):
        return (
            f"<SuburbDemographics(suburb_id={self.suburb_id}, "
            f"population_18_25={self.population_18_25})>"
        )
