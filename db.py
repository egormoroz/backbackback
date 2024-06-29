from datetime import date
from typing import Sequence

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import exists, select, update

from settings import settings
from models import Role, metadata_inst, EmployeeORM

engine = create_async_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=False,
)

session = async_sessionmaker(engine)


async def create_tables():
    async with engine.connect() as conn:
        await conn.run_sync(metadata_inst.drop_all)
        await conn.run_sync(metadata_inst.create_all)
        await conn.commit()


async def insert_data(experience: int = 666):
    employee = EmployeeORM(id=1337_696969, role=Role.admin, 
                           experience=experience, email="bob@email.org",)
    async with session() as sess:
        sess.add(employee)
        await sess.commit()


# Should I return ORM or DTO?
async def get_empl(id: int) -> EmployeeORM | None:
    async with session() as sess:
        query = select(EmployeeORM).filter(
                EmployeeORM.id == id, EmployeeORM.removed_on == None)
        res = await sess.execute(query)
        return res.scalar_one_or_none()


# page_idx starts with zero
async def get_empls_page(page_idx: int, page_size: int) -> Sequence[EmployeeORM]:
    async with session() as sess:
        query = (select(EmployeeORM)
            .offset(page_idx*page_idx)
            .limit(page_size)
            .filter(EmployeeORM.removed_on == None)
        )
        res = await sess.execute(query)
        return res.scalars().all()


async def upsert_empl(empl: EmployeeORM):
    async with session() as sess:
        query = select(exists(EmployeeORM).where(EmployeeORM.id == empl.id))
        res = await sess.execute(query)
        if res.scalar():
            await update_empl(empl)
        else:
            sess.add(empl)
            await sess.commit()


async def update_empl(empl: EmployeeORM) -> bool:
    async with session() as sess:
        stmt = (update(EmployeeORM)
            .where(EmployeeORM.id == empl.id)
            .values(**empl.as_dict(ignore=["id"]))
        )
        # TODO: does double await here make sense???
        res = await sess.execute(stmt)
        await sess.commit()
        return res.rowcount > 0


async def remove_empl(id: int):
    async with session() as sess:
        stmt = (update(EmployeeORM)
            .where(EmployeeORM.id == id)
            .values(removed_on=date.today())
        )
        # TODO: does double await here make sense???
        await sess.execute(stmt)
        await sess.commit()

