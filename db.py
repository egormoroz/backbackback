from datetime import date
from typing import Sequence
from sqlalchemy import create_engine, exists, select, update
from sqlalchemy.orm import sessionmaker

from settings import settings
from models import Role, metadata_inst, EmployeeORM

from schemas import EmployeeDTO

engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=False,
)

session = sessionmaker(engine)


def create_tables():
    with engine.connect() as conn:
        metadata_inst.drop_all(conn)
        metadata_inst.create_all(conn)
        conn.commit()


def insert_data(experience: int = 666):
    employee = EmployeeORM(id=1337_696969, role=Role.admin, 
                           experience=experience, email="bob@email.org",)
    with session() as sess:
        sess.add(employee)
        sess.commit()


# Should I return ORM or DTO?
def get_empl(id: int) -> EmployeeORM | None:
    with session() as sess:
        query = select(EmployeeORM).filter(
                EmployeeORM.id == id, EmployeeORM.removed_on == None)
        return sess.execute(query).scalar_one_or_none()


# page_idx starts with zero
def get_empls_page(page_idx: int, page_size: int) -> Sequence[EmployeeORM]:
    with session() as sess:
        query = (select(EmployeeORM)
            .offset(page_idx*page_idx)
            .limit(page_size)
            .filter(EmployeeORM.removed_on == None)
        )
        return sess.execute(query).scalars().all()


# db agnostic upsert
def upsert_empl(empl: EmployeeORM):
    with session() as sess:
        query = exists(EmployeeORM).where(EmployeeORM.id == empl.id)
        if sess.query(query).scalar():
            update_empl(empl)
        else:
            sess.add(empl)
            sess.commit()


def update_empl(empl: EmployeeORM) -> bool:
    with session() as sess:
        stmt = (update(EmployeeORM)
            .where(EmployeeORM.id == empl.id)
            .values(**empl.as_dict(ignore=["id"]))
        )
        res = sess.execute(stmt)
        sess.commit()
        return res.rowcount > 0


def remove_empl(id: int):
    with session() as sess:
        stmt = (update(EmployeeORM)
            .where(EmployeeORM.id == id)
            .values(removed_on=date.today())
        )
        sess.execute(stmt)
        sess.commit()



create_tables()

if __name__ == "__main__":
    insert_data()
    upsert_empl(EmployeeORM(id=1337_696968, email="meow"))

    with session() as sess:
        res = sess.execute(select(EmployeeORM))
        res_orm = res.scalars().all()
        print(f'{res_orm=}')

        res_dto = [EmployeeDTO.model_validate(row, from_attributes=True) 
                   for row in res_orm]
        print(res_dto)


