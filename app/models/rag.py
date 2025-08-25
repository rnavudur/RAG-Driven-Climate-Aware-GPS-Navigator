from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.core.database import Base
import uuid
from datetime import datetime


class KnowledgeDocument(Base):
    """Knowledge documents for RAG explanations (NWS alerts, FEMA guides, etc.)."""
    __tablename__ = "knowledge_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Document metadata
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    document_type = Column(String(100), nullable=False)  # nws_alert, fema_guide, etc.
    source = Column(String(100), nullable=False)  # NWS, FEMA, USGS, etc.
    source_url = Column(Text)
    
    # Geographic scope
    geom = Column(Geometry('POLYGON', srid=4326))  # Geographic coverage area
    h3_cells = Column(JSONB)  # H3 geohash cells for fast spatial lookup
    
    # Temporal scope
    effective_start = Column(DateTime)
    effective_end = Column(DateTime)
    published_at = Column(DateTime)
    
    # Content analysis
    hazard_types = Column(JSONB)  # List of hazard types mentioned
    severity_levels = Column(JSONB)  # Severity levels mentioned
    keywords = Column(JSONB)  # Extracted keywords
    
    # Vector embeddings
    embedding_vector = Column(Text)  # Base64 encoded embedding vector
    
    # Metadata
    properties = Column(JSONB)  # Additional properties
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_knowledge_docs_type', 'document_type'),
        Index('idx_knowledge_docs_source', 'source'),
        Index('idx_knowledge_docs_hazards', 'hazard_types', postgresql_using='gin'),
        Index('idx_knowledge_docs_keywords', 'keywords', postgresql_using='gin'),
        Index('idx_knowledge_docs_geom', 'geom', postgresql_using='gist'),
        Index('idx_knowledge_docs_temporal', 'effective_start', 'effective_end'),
    )


class DocumentChunk(Base):
    """Chunked sections of knowledge documents for better retrieval."""
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('knowledge_documents.id'), nullable=False)
    
    # Chunk content
    chunk_text = Column(Text, nullable=False)
    chunk_order = Column(Integer, nullable=False)  # Order within document
    chunk_type = Column(String(50))  # header, paragraph, instruction, etc.
    
    # Vector embeddings for this chunk
    embedding_vector = Column(Text, nullable=False)  # Base64 encoded
    
    # Chunk metadata
    start_char = Column(Integer)  # Character position in original document
    end_char = Column(Integer)
    
    # Relationships
    document = relationship("KnowledgeDocument")
    
    # Indexes
    __table_args__ = (
        Index('idx_document_chunks_doc', 'document_id'),
        Index('idx_document_chunks_order', 'document_id', 'chunk_order'),
    )


class RouteExplanation(Base):
    """Generated explanations for routes with source citations."""
    __tablename__ = "route_explanations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(UUID(as_uuid=True), ForeignKey('routes.id'), nullable=False)
    
    # Explanation content
    explanation_markdown = Column(Text, nullable=False)
    explanation_text = Column(Text, nullable=False)
    
    # Risk summary
    risk_summary = Column(Text)
    avoided_hazards_summary = Column(Text)
    safety_benefits = Column(Text)
    
    # Source citations
    source_documents = Column(JSONB)  # List of cited documents with relevance scores
    source_chunks = Column(JSONB)  # Specific chunks used for explanation
    
    # Generation metadata
    model_used = Column(String(100))  # LLM model used
    generation_timestamp = Column(DateTime, default=datetime.utcnow)
    confidence_score = Column(Float)
    
    # Relationships
    route = relationship("Route")
    
    # Indexes
    __table_args__ = (
        Index('idx_route_explanations_route', 'route_id'),
        Index('idx_route_explanations_timestamp', 'generation_timestamp'),
    )


class ExplanationTemplate(Base):
    """Templates for generating route explanations."""
    __tablename__ = "explanation_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Template metadata
    name = Column(String(200), nullable=False)
    description = Column(Text)
    template_type = Column(String(100))  # route_comparison, hazard_avoidance, etc.
    
    # Template content
    system_prompt = Column(Text, nullable=False)
    user_prompt_template = Column(Text, nullable=False)
    example_output = Column(Text)
    
    # Template parameters
    required_variables = Column(JSONB)  # Variables that must be provided
    optional_variables = Column(JSONB)  # Optional variables
    
    # Usage metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_explanation_templates_type', 'template_type'),
        Index('idx_explanation_templates_active', 'is_active'),
    ) 