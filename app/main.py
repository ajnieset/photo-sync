from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Base.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)
