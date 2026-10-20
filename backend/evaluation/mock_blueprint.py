"""
Mock Exam Blueprint Specifications for GPAT 2027 Evaluation Engine.

Separates PROVISIONAL_MOCK from OFFICIAL_EXAM_SIMULATION.
Configurable blueprint controlling:
- Total questions & duration
- Marking scheme (+marks, -negative marks)
- Subject and difficulty distribution
- Question selection constraints (exposure windows, no duplicates)
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

@dataclass
class MockBlueprint:
    name: str = "GPAT_PROVISIONAL_MOCK_V1"
    exam_version: str = "PROVISIONAL_MOCK"  # PROVISIONAL_MOCK vs OFFICIAL_EXAM_SIMULATION
    title: str = "GPAT 2027 Full Length Pharmacology Simulation"
    total_questions: int = 25  # Scalable up to 125 based on available bank
    duration_minutes: int = 45 # Standard ~1.8 min per question
    marks_per_question: float = 4.0
    negative_marks: float = 1.0
    difficulty_distribution: Dict[str, float] = field(default_factory=lambda: {
        "easy": 0.25,      # difficulty <= 6
        "medium": 0.50,    # difficulty 7-8
        "hard": 0.25       # difficulty >= 9
    })
    exposure_avoid_last_n_days: int = 3
    allow_unverified_questions: bool = False
    enforce_four_quadrant_coverage: bool = True  # Recall, Mechanism, Application, Discrimination
    selected_topic_ids: Optional[List[str]] = None
    selected_subject_ids: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "exam_version": self.exam_version,
            "title": self.title,
            "total_questions": self.total_questions,
            "duration_minutes": self.duration_minutes,
            "duration_seconds": self.duration_minutes * 60,
            "marks_per_question": self.marks_per_question,
            "negative_marks": self.negative_marks,
            "difficulty_distribution": self.difficulty_distribution,
            "exposure_avoid_last_n_days": self.exposure_avoid_last_n_days,
            "allow_unverified_questions": self.allow_unverified_questions,
            "enforce_four_quadrant_coverage": self.enforce_four_quadrant_coverage,
            "selected_topic_ids": self.selected_topic_ids,
            "selected_subject_ids": self.selected_subject_ids
        }

# Pre-configured blueprints
PROVISIONAL_MOCK_25 = MockBlueprint(
    name="GPAT_PROVISIONAL_MOCK_25",
    exam_version="PROVISIONAL_MOCK",
    title="GPAT 2027 Sprint Mock (25 Questions)",
    total_questions=25,
    duration_minutes=45,
    marks_per_question=4.0,
    negative_marks=1.0
)

PROVISIONAL_MOCK_FULL = MockBlueprint(
    name="GPAT_PROVISIONAL_MOCK_FULL",
    exam_version="PROVISIONAL_MOCK",
    title="GPAT Comprehensive Pharmacology Mock",
    total_questions=40,
    duration_minutes=75,
    marks_per_question=4.0,
    negative_marks=1.0
)

OFFICIAL_GPAT_125 = MockBlueprint(
    name="OFFICIAL_GPAT_125",
    exam_version="OFFICIAL_EXAM_SIMULATION",
    title="GPAT 2027 Full Official Exam Simulation (125 Questions)",
    total_questions=125,
    duration_minutes=180,
    marks_per_question=4.0,
    negative_marks=1.0,
    exposure_avoid_last_n_days=0
)

BLUEPRINTS: Dict[str, MockBlueprint] = {
    "default": PROVISIONAL_MOCK_25,
    "sprint_25": PROVISIONAL_MOCK_25,
    "full_40": PROVISIONAL_MOCK_FULL,
    "official_125": OFFICIAL_GPAT_125,
    "gpat_125": OFFICIAL_GPAT_125
}
