from sqlalchemy import Column, String, DateTime, Float, JSON, Text, Boolean
from app.database import Base
import uuid
from datetime import datetime

class CVE(Base):
    __tablename__ = "cves"
    
    # Change UUID to String for SQLite compatibility
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cve_id = Column(String(20), unique=True, nullable=False, index=True)
    published_date = Column(DateTime)
    modified_date = Column(DateTime)
    description = Column(Text)
    cvss_v3_score = Column(Float)
    cvss_v3_vector = Column(String(100))
    severity_level = Column(String(10))
    cwe_ids = Column(JSON)
    affected_products = Column(JSON)
    references = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,  # Already a string now
            "cve_id": self.cve_id,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "modified_date": self.modified_date.isoformat() if self.modified_date else None,
            "description": self.description,
            "cvss_v3_score": self.cvss_v3_score,
            "cvss_v3_vector": self.cvss_v3_vector,
            "severity_level": self.severity_level,
            "cwe_ids": self.cwe_ids,
            "affected_products": self.affected_products,
            "references": self.references,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
