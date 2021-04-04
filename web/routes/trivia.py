from os import getenv

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import FileResponse
from starlette.responses import RedirectResponse

router = APIRouter()
