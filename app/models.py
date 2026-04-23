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


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(120), nullable=False)
    sort_order = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, nullable=False, default=True)

    guides = relationship("Guide", back_populates="topic")

    def __repr__(self):
        return f"<Topic(id={self.id}, slug='{self.slug}')>"


class Arc(Base):
    __tablename__ = "arcs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(120), nullable=False)
    sort_order = Column(Integer, nullable=False, default=1)
    timeframe_label = Column(String(50), nullable=False)

    guides = relationship("Guide", back_populates="arc")

    def __repr__(self):
        return f"<Arc(id={self.id}, slug='{self.slug}')>"


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
    sa2_code = Column(
        String(20),
        ForeignKey("suburb_demographics.sa2_code"),
        nullable=True,
        index=True,
    )
    sa3_name = Column(String(120), nullable=True, index=True)

    demographic = relationship("SuburbDemographic", back_populates="suburbs")

    def __repr__(self):
        return f"<Suburb(id={self.id}, name='{self.name}', postcode='{self.postcode}')>"


class Guide(Base):
    __tablename__ = "guides"
    __table_args__ = (
        UniqueConstraint("arc_id", "arc_order", name="uq_guides_arc_order"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False, unique=True, index=True)
    arc_id = Column(Integer, ForeignKey("arcs.id"), nullable=False, index=True)
    arc_order = Column(Integer, nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"),
                      nullable=False, index=True)
    next_guide_id = Column(Integer, ForeignKey(
        "guides.id"), nullable=True, index=True)
    near_me_deeplink = Column(String(300), nullable=False)
    reading_time_min = Column(Integer, nullable=False, default=3)
    is_published = Column(Boolean, nullable=False, default=True)
    is_featured = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    arc = relationship("Arc", back_populates="guides")
    topic = relationship("Topic", back_populates="guides")
    sections = relationship(
        "GuideSection",
        back_populates="guide",
        cascade="all, delete-orphan",
        order_by="GuideSection.section_order",
    )
    next_guide = relationship("Guide", remote_side=[id], uselist=False)

    def __repr__(self):
        return f"<Guide(id={self.id}, slug='{self.slug}', arc_order={self.arc_order})>"


class GuideSection(Base):
    __tablename__ = "guide_sections"
    __table_args__ = (
        UniqueConstraint("guide_id", "section_key",
                         name="uq_guide_sections_key"),
        UniqueConstraint("guide_id", "section_order",
                         name="uq_guide_sections_order"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    guide_id = Column(Integer, ForeignKey("guides.id"),
                      nullable=False, index=True)
    section_key = Column(String(50), nullable=False)
    section_order = Column(Integer, nullable=False)
    body = Column(Text, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    guide = relationship("Guide", back_populates="sections")

    def __repr__(self):
        return f"<GuideSection(id={self.id}, guide_id={self.guide_id}, key='{self.section_key}')>"


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

    suburbs = relationship("Suburb", back_populates="demographic")

    def __repr__(self):
        return f"<SuburbDemographic(sa2_code='{self.sa2_code}', sa2_name='{self.sa2_name}')>"
