import annotated_types as at
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, HTTPException, status
from loguru import logger


import db
from models import EmployeeORM
from schemas import EmployeeDTO


@asynccontextmanager
async def lifespan(_: FastAPI):
    await db.create_tables()
    await db.insert_data()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/employee/{id}")
async def get_employee(id: Annotated[int, at.Ge(0)]):
    logger.info(f'Get employee by {id=}')
    empl = await db.get_empl(id)
    if empl is None:
        logger.error(f'Tried to get nonexistant employee by {id=}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return empl.as_dict()


# somehow doens't work with Path
@app.get("/employee")
async def get_employees_page(
    current_page: Annotated[int, at.Ge(1)], 
    page_size: Annotated[int, at.Ge(1)],
):
    logger.info(f'Retrieve a page of employees [{current_page}:{page_size}]')
    page = await db.get_empls_page(current_page-1, page_size)
    return [empl.as_dict() for empl in page ]


@app.post("/employee")
async def post_employee(empl: EmployeeDTO):
    # hacky
    logger.info(f"Upsert employee with {empl.id=}")
    orm = EmployeeORM(**empl.__dict__)
    await db.upsert_empl(orm)


@app.patch("/employee")
async def update_employee(empl: EmployeeDTO):
    logger.info(f"Update employee with {empl.id=}")
    orm = EmployeeORM(**empl.__dict__)
    ok = await db.update_empl(orm)
    if not ok:
        logger.error(f'Tried to update nonexistant employee with {empl.id=}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.delete("/employee/{id}")
async def delete_employee(id: Annotated[int, at.Ge(0)]):
    logger.info(f"Delete employee with {id=}")
    await db.remove_empl(id)
