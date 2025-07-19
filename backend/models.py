from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, BLOB
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class Workorder(Base):
    __tablename__ = 'workorders'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default='uploaded')
    original_file_path = Column(String, nullable=False)
    leads = relationship('Lead', back_populates='workorder')

class Lead(Base):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True, index=True)
    workorder_id = Column(Integer, ForeignKey('workorders.id'))
    data = Column(JSON, nullable=False)
    raw_webpage_text = Column(Text, nullable=True)  # New field for scraped text
    buyer_persona = Column(Text, nullable=True)  # New field for generated persona
    buyer_persona_embedding = Column(BLOB, nullable=True)  # Store as bytes for sqlite-vec
    cluster_id = Column(Integer, nullable=True)  # Cluster ID assigned by clustering algorithm
    company_name = Column(String, nullable=True)  # Company name extracted from data
    display_order = Column(Integer, nullable=True)  # Display order for persistent reranking
    status = Column(String, nullable=True, default='unchecked')  # Lead status (unchecked, converted, failed, in-progress)
    workorder = relationship('Workorder', back_populates='leads') 