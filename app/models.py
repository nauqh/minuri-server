from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)

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
    sa3_name = Column(String(120), nullable=True, index=True)

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


class SuburbDemographic(Base):
    __tablename__ = "suburb_demographics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sa2_code = Column(String(20), nullable=False, unique=True, index=True)
    sa2_name = Column(String(120), nullable=False, index=True)
    sa3_name = Column(String(120), nullable=False, index=True)
    sa4_name = Column(String(120), nullable=False, index=True)
    gccsa_name = Column(String(120), nullable=False, index=True)
    erp_2024 = Column(Integer, nullable=True)
    erp_2025 = Column(Integer, nullable=True)
    erp_change_no = Column(Integer, nullable=True)
    erp_change_pct = Column(Float, nullable=True)
    area_km2 = Column(Float, nullable=True)
    pop_density_2025 = Column(Float, nullable=True)

    def __repr__(self):
        return f"<SuburbDemographic(sa2_code='{self.sa2_code}', sa2_name='{self.sa2_name}')>"
