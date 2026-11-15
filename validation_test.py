from pydantic import BaseModel, ValidationError

from analyzer import parse_response
from schemas import DocumentAnalysis


class TestSchema(BaseModel):
    title: str
    summary: str


response = """Here is JSON: {"title": "Report"}"""
analysis = parse_response(response, TestSchema)
print(f"PARSING TEST: {analysis}")

invalid_data = {
    "title": "Business Report",
    "summary": "Revenue increased",
    "key_points": "Revenue increased by 20%",
    "entities": [],
    "document_type": "report",
    "risks_or_concerns": []
}

try:
    analysiss = DocumentAnalysis.model_validate(invalid_data)
    print(f"PYDANTIC TEST: {analysiss}")
except ValidationError as e:
    print(f"PYDANTIC TEST: {e}")
