from fastapi import FastAPI
import uvicorn

from app.api.report import router as report_router


app = FastAPI(title="Report Export API")
app.include_router(report_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8080, reload=True)
