import asyncio
import enum
import json
from typing import Dict, List
from uuid import UUID, uuid4
from concurrent.futures.process import ProcessPoolExecutor

import numpy as np
import pydantic
import uvicorn
from fastapi import FastAPI, BackgroundTasks, status
from fastapi.responses import JSONResponse


app = FastAPI(
    debug=True,
    title="High-load Calculator"
)


class Status(enum.Enum):
    """Task status."""
    ON = "ON"
    END = "END"


class Calculation(pydantic.BaseModel):
    """Calculation unit model."""
    uid: UUID = pydantic.Field(default_factory=uuid4)
    status: Status = Status.ON.value
    result: pydantic.Json[List[float]] = None


calcs: Dict[str, Calculation] = {}


async def calculate(X: int, uid: UUID):
    """Computing a random matrix X by X."""
    await asyncio.sleep(20)  # Sleep for tests.
    calcs[uid].result = json.dumps(np.random.rand(X, X).tolist())


async def run_in_process(fn, *args):
    """Run in a separate process."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(app.state.executor, fn, *args)


async def start_task(X: int, uid: UUID):
    """Init task."""
    calcs[uid].result = await run_in_process(calculate, X)
    calcs[uid].status = Status.END.value


@app.get(
    "/calculate",
    status_code=status.HTTP_201_CREATED,
)
async def get_calculate(
    X: int,
    background_tasks: BackgroundTasks
) -> int:
    """
    Calculate random matrix X by X.

    Returns:
        Task UUID.
    """
    new_calc = Calculation()
    calcs[new_calc.uid] = new_calc
    background_tasks.add_task(start_task, X, new_calc.uid)
    return new_calc.uid


@app.get("/result")
async def get_result(uid: UUID) -> Dict:
    """
    Get current calc result for matrix by task UUID.

    Returns:
        Matrix or nothing.
    """
    if calcs[uid].status == Status.END.value:
        return calcs[uid].result
    return JSONResponse(content="", status_code=201)


@app.on_event("startup")
async def startup_event():
    """Starting the asynchronous execution of requests."""
    app.state.executor = ProcessPoolExecutor()


@app.on_event("shutdown")
async def on_shutdown():
    """Ending the asynchronous execution of requests."""
    app.state.executor.shutdown()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8082,
        reload=True,
        debug=True,
    )
