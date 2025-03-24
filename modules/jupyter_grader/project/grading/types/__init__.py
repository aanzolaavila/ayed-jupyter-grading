from typing import Any
from abc import ABC, abstractmethod

from ..utils import validation

class Student:
    def __init__(self, name: str, code: int) -> None:
        validation.validate_student(name, code)
        self.name: str = name
        self.code: int = code

class Checker(ABC):
    def __init__(self, name: str, code: int) -> None:
        self.student = Student(name, code)
        super().__init__()

    @abstractmethod
    def grade(self, part: str, answer: Any):
        pass

class GraderException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
