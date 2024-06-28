import enum
from datetime import date
from sqlalchemy import (
    VARCHAR, Enum, Table, Column, BigInteger, SmallInteger, Date, MetaData
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

metadata_inst = MetaData()

class Base(DeclarativeBase):
    pass


class Role(enum.Enum):
    admin = "admin"
    worker = "worker"


class EmployeeORM(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[Role]
    email: Mapped[str]
    experience: Mapped[int]
    removed_on: Mapped[date | None]

    def as_dict(self, ignore=[]):
        ignore += ["_sa_instance_state"]
        return {
            k: v for k, v in self.__dict__.items()
            if v is not None and not k in ignore
        }


employees_table = Table(
    "employees",
    metadata_inst,
    Column("id", BigInteger, primary_key=True),
    Column("role", Enum(Role)),
    Column("email", VARCHAR(256)),
    Column("experience", SmallInteger),
    Column("removed_on", Date),
)

