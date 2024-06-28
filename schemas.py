from pydantic import BaseModel, EmailStr
from models import Role
from datetime import date

from typing import Annotated
import annotated_types as at


class EmployeeDTO(BaseModel):
    id: int
    role: Role | None
    email: EmailStr | None
    experience: Annotated[int, at.Ge(0)] | None
    removed_on: date | None

