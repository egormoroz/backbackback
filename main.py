import annotated_types as at
from typing import Annotated
from fastapi import FastAPI, HTTPException, status
from loguru import logger
import db

from models import EmployeeORM
from schemas import EmployeeDTO

db.insert_data()

app = FastAPI()


def orm2dto(empl: EmployeeORM) -> EmployeeDTO:
    return EmployeeDTO.model_validate(empl, from_attributes=True)


@app.get("/employee/{id}")
def get_employee(id: Annotated[int, at.Ge(0)]):
    logger.info(f'Get employee by {id=}')
    empl = db.get_empl(id)
    if empl is None:
        logger.error(f'Tried to get nonexistant employee by {id=}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return empl.as_dict()


# somehow doens't work with Path
@app.get("/employee")
def get_employees_page(
    current_page: Annotated[int, at.Ge(1)], 
    page_size: Annotated[int, at.Ge(1)],
):
    logger.info(f'Retrieve a page of employees [{current_page}:{page_size}]')
    page = db.get_empls_page(current_page-1, page_size)
    return [empl.as_dict() for empl in page ]


@app.post("/employee")
def post_employee(empl: EmployeeDTO):
    # hacky
    logger.info(f"Upsert employee with {empl.id=}")
    orm = EmployeeORM(**empl.__dict__)
    db.upsert_empl(orm)


@app.patch("/employee")
def update_employee(empl: EmployeeDTO):
    logger.info(f"Update employee with {empl.id=}")
    orm = EmployeeORM(**empl.__dict__)
    if not db.update_empl(orm):
        logger.error(f'Tried to update nonexistant employee with {empl.id=}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.delete("/employee/{id}")
def delete_employee(id: Annotated[int, at.Ge(0)]):
    logger.info(f"Delete employee with {id=}")
    db.remove_empl(id)
