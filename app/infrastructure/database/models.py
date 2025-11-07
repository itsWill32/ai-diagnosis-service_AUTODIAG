# ============================================
# AI-DIAGNOSIS SERVICE - SQLALCHEMY MODELS
# AutoDiag Project - Python/FastAPI
# ============================================

from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean, DateTime, 
    Text, JSON, ForeignKey, Enum as SQLEnum, ARRAY
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import uuid

Base = declarative_base()

# ============================================
# ENUMS (Value Objects)
# ============================================

class MessageRole(str, enum.Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"

class UrgencyLevel(str, enum.Enum):
    CRITICAL = "CRITICAL"
    MODERATE = "MODERATE"
    LOW = "LOW"

class ProblemCategory(str, enum.Enum):
    ENGINE = "ENGINE"
    BRAKES = "BRAKES"
    TRANSMISSION = "TRANSMISSION"
    SUSPENSION = "SUSPENSION"
    ELECTRICAL = "ELECTRICAL"
    COOLING_SYSTEM = "COOLING_SYSTEM"
    EXHAUST = "EXHAUST"
    FUEL_SYSTEM = "FUEL_SYSTEM"
    STEERING = "STEERING"
    TIRES = "TIRES"
    BATTERY = "BATTERY"
    LIGHTS = "LIGHTS"
    OTHER = "OTHER"

class SentimentType(str, enum.Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"

class ReportType(str, enum.Enum):
    COMMON_PROBLEMS = "COMMON_PROBLEMS"
    MODEL_ACCURACY = "MODEL_ACCURACY"
    SENTIMENT_AGGREGATED = "SENTIMENT_AGGREGATED"
    RECOMMENDATION_EFFECTIVENESS = "RECOMMENDATION_EFFECTIVENESS"
    GENERAL_STATS = "GENERAL_STATS"

class ExportFormat(str, enum.Enum):
    PDF = "PDF"
    EXCEL = "EXCEL"
    JSON = "JSON"

# ============================================
# AGGREGATE ROOT: DiagnosisSession
# ============================================

class DiagnosisSession(Base):
    __tablename__ = "diagnosis_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)  # Auth Service reference
    vehicle_id = Column(String, nullable=False, index=True)  # Vehicle Service reference
    
    # Diagnosis result (JSON - DiagnosisResult VO)
    diagnosis_result = Column(JSON, nullable=True)
    
    # UrgencyLevel VO
    urgency_level = Column(SQLEnum(UrgencyLevel), nullable=True)
    urgency_score = Column(Integer, nullable=True)  # 0-100
    
    # Cost estimate (CostEstimate VO)
    min_cost_amount = Column(Numeric(10, 2), nullable=True)
    max_cost_amount = Column(Numeric(10, 2), nullable=True)
    cost_currency = Column(String, default="MXN")
    cost_breakdown = Column(JSON, nullable=True)  # Array de CostBreakdown
    
    # ML model version tracking
    model_version = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    was_shared = Column(Boolean, default=False)
    generated_appointment = Column(Boolean, default=False)
    appointment_id = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    last_activity_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Relationships (Child Entities)
    messages = relationship("DiagnosisMessage", back_populates="session", cascade="all, delete-orphan")
    problem_classifications = relationship("ProblemClassification", back_populates="session", cascade="all, delete-orphan")
    workshop_recommendations = relationship("WorkshopRecommendation", back_populates="session", cascade="all, delete-orphan")

# ============================================
# CHILD ENTITY: DiagnosisMessage
# ============================================

class DiagnosisMessage(Base):
    __tablename__ = "diagnosis_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("diagnosis_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    role = Column(SQLEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    
    # Tracking
    tokens_consumed = Column(Integer, nullable=True)
    metadata = Column(JSON, nullable=True)
    triggered_classification = Column(Boolean, default=False)
    
    # Attachments
    has_attachments = Column(Boolean, default=False)
    attachment_urls = Column(ARRAY(String), default=[])
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationship
    session = relationship("DiagnosisSession", back_populates="messages")

# ============================================
# CHILD ENTITY: ProblemClassification
# ============================================

class ProblemClassification(Base):
    __tablename__ = "problem_classifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("diagnosis_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # ProblemCategory VO
    category = Column(SQLEnum(ProblemCategory), nullable=False)
    subcategory = Column(String, nullable=True)
    
    # ConfidenceScore VO
    confidence_score = Column(Numeric(4, 3), nullable=False)  # 0.000 - 1.000
    
    # Alternative categories (JSON array)
    alternative_categories = Column(JSON, nullable=True)
    
    # Features extracted
    features_extracted = Column(JSON, nullable=True)
    
    # ML model tracking
    model_version = Column(String, nullable=False)
    classified_at = Column(DateTime(timezone=True), server_default=func.now())
    processing_time_ms = Column(Integer, nullable=True)
    
    # Feedback loop
    was_corrected = Column(Boolean, default=False)
    corrected_category = Column(SQLEnum(ProblemCategory), nullable=True)
    
    # Relationship
    session = relationship("DiagnosisSession", back_populates="problem_classifications")

# ============================================
# CHILD ENTITY: WorkshopRecommendation
# ============================================

class WorkshopRecommendation(Base):
    __tablename__ = "workshop_recommendations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("diagnosis_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    workshop_id = Column(String, nullable=False, index=True)  # Workshop Service reference
    
    # Recommendation details
    recommendation_score = Column(Numeric(4, 3), nullable=False)  # 0.000 - 1.000
    rank_position = Column(Integer, nullable=False)  # 1-5
    reasons = Column(JSON, nullable=False)  # Razones de la recomendación
    
    # Distance
    distance_km = Column(Numeric(6, 2), nullable=True)
    
    # Features used
    features_used = Column(JSON, nullable=True)
    
    # ML model tracking
    model_version = Column(String, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Effectiveness tracking
    was_selected = Column(Boolean, default=False)
    generated_appointment = Column(Boolean, default=False)
    
    # Relationship
    session = relationship("DiagnosisSession", back_populates="workshop_recommendations")

# ============================================
# AGGREGATE ROOT: SentimentAnalysis
# ============================================

class SentimentAnalysis(Base):
    __tablename__ = "sentiment_analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id = Column(String, unique=True, nullable=False, index=True)  # Workshop Service reference
    
    # Sentiment VO
    sentiment = Column(SQLEnum(SentimentType), nullable=False)
    confidence_score = Column(Numeric(4, 3), nullable=False)  # 0.000 - 1.000
    sentiment_scores = Column(JSON, nullable=False)  # {positive: 0.12, neutral: 0.08, negative: 0.80}
    
    # Aspects mentioned
    aspects_mentioned = Column(JSON, nullable=True)  # Array de aspectos detectados
    key_words = Column(JSON, nullable=True)  # Array de palabras clave
    
    # ML model tracking
    model_version = Column(String, nullable=False)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    processing_time_ms = Column(Integer, nullable=True)
    
    # Feedback loop
    was_corrected = Column(Boolean, default=False)

# ============================================
# AGGREGATE ROOT: AnalyticsReport
# ============================================

class AnalyticsReport(Base):
    __tablename__ = "analytics_reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    report_type = Column(SQLEnum(ReportType), nullable=False, index=True)
    
    # Period
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Report data (JSON)
    report_data = Column(JSON, nullable=False)
    
    # Generated by
    generated_by = Column(String, nullable=False)  # userId (Admin)
    
    # Export
    export_format = Column(SQLEnum(ExportFormat), nullable=True)
    file_url = Column(String, nullable=True)
    
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)