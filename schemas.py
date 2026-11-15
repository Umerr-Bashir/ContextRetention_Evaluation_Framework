from pydantic import BaseModel, Field

class Entity(BaseModel):
    name: str
    entity_type: str
    description: str

class DocumentAnalysis(BaseModel):
    title: str
    summary: str
    key_points: list[str]
    entities: list[Entity]
    document_type: str
    risks_or_concerns: list[str]