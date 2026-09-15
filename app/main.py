from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.auth import get_optional_user
from app.api.auth import router as auth_router
from app.api.solves import router as solves_router
from app.core.config import settings
from app.core.database import Base, engine
from app.models.user import User


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema asynchronously on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup connection pool on shutdown
    await engine.dispose()


app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan)


# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# Mount static assets
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Register API routers
app.include_router(auth_router)
app.include_router(solves_router)


# Favicon endpoint
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    svg_icon = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        '<rect width="100" height="100" rx="20" fill="#0d1117"/>'
        '<path d="M25 25h20v20H25zm25 0h20v20H50zm25 0h20v20H75z'
        "M25 50h20v20H25zm25 0h20v20H50zm25 0h20v20H75z"
        'M25 75h20v20H25zm25 75h20v20H50zm25 75h20v20H75z" fill="#00f0ff" opacity="0.9"/>'
        "</svg>"
    )
    return Response(content=svg_icon, media_type="image/svg+xml")


@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request, user: User | None = Depends(get_optional_user)):
    # Guests can access the timer freely without registration
    return templates.TemplateResponse(request=request, name="index.html", context={"user": user})


@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request, user: User | None = Depends(get_optional_user)):
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request=request, name="history.html", context={"user": user})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, user: User | None = Depends(get_optional_user)):
    if user:
        return RedirectResponse(url="/")
    return templates.TemplateResponse(request=request, name="login.html", context={"user": None})
