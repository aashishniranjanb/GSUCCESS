from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class StudyRepository(ABC):
    @abstractmethod
    def get_or_create_daily_session(self, user_id: str, session_date: str, target_minutes: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def persist_daily_session(self, user_id: str, session_date: str, target_minutes: int, questions: List[Dict[str, Any]]) -> str:
        pass

    @abstractmethod
    def update_session_item_result(self, user_id: str, question_id: str, is_correct: bool, cur: Optional[Any] = None):
        pass

    @abstractmethod
    def log_learning_event(self, user_id: str, event_type: str, question_id: Optional[str] = None,
                           concept_id: Optional[str] = None, payload: Optional[Dict[str, Any]] = None, cur: Optional[Any] = None) -> str:
        pass
