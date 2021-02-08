import asyncio
import enum
import json
from typing import List, Dict
from uuid import UUID, uuid4


import numpy as np
import pydantic
from fastapi import APIRouter, BackgroundTasks, status
from fastapi.responses import JSONResponse

router = APIRouter()


class Status(enum.Enum):
    ON = "ON"
    END = "END"


class Calculation(pydantic.BaseModel):
    uid: UUID = pydantic.Field(default_factory=uuid4)
    status: Status = Status.ON
    result: pydantic.Json[List[float]] = None


calcs: Dict[str, Calculation] = {}


async def run_in_process(fn, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(router.state.executor, fn, *args)


async def calculate(X: int, uid: int,):
    await asyncio.sleep(20)
    calcs[uid].result = json.dumps(np.random.rand(X, X).tolist())


async def start_cpu_bound_task(uid: UUID, X: int) -> None:
    calcs[uid].result = await run_in_process(calculate, X)
    calcs[uid].status = Status.END.value


@router.get(
    "/calculate",
    status_code=status.HTTP_201_CREATED,
)
async def get_calculate(
    X: int,
    background_tasks: BackgroundTasks
) -> int:
    new_calc = Calculation()
    calcs[new_calc.uid] = new_calc
    background_tasks.add_task(calculate, X, new_calc.uid)
    return new_calc.uid


@router.get("/result")
async def get_result(uid: UUID) -> Dict:
    if calcs[uid].result is not None:
        return calcs[uid].result
    return JSONResponse(content="", status_code=201)
