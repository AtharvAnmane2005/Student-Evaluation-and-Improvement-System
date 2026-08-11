from app.models.assessment import AssessmentInDB
from app.repositories.base import BaseRepository


class AssessmentRepository(BaseRepository[AssessmentInDB]):
    collection_name = "assessments"
    model = AssessmentInDB
