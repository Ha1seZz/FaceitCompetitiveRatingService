from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import uvicorn
from app.api import router as api_router  # Импорт основного роутера API v1


app = FastAPI(title="Faceit Competitive Rating Service")
app.include_router(api_router)


@app.exception_handler(httpx.HTTPStatusError)
async def httpx_status_error_handler(request: Request, exc: httpx.HTTPStatusError):
    return JSONResponse(
        status_code=exc.response.status_code,
        content={"detail": f"External API error: {exc.response.text}"},
    )


if __name__ == "__main__":  # Точка входа для запуска приложения
    uvicorn.run("app.main:app", reload=True)
