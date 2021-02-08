from concurrent.futures.process import ProcessPoolExecutor

import uvicorn
from fastapi import FastAPI

import endpoints


def rest():
    app = FastAPI(
        debug=True,
        title="Calculator"
    )

    app.include_router(
        endpoints.router,
        tags=["endpoints"],
    )
    return app


app = rest()


@app.on_event("startup")
async def startup_event():
    """Событие при запуске."""
    # Запуск асинхронного выполнения запросов.
    app.state.executor = ProcessPoolExecutor()


@app.on_event("shutdown")
async def on_shutdown():
    """Событие при отключение."""
    app.state.executor.shutdown()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8082,
        reload=True,
        debug=True,
    )
