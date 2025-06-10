from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import secrets

import sys   #FIXME
from pathlib import Path #FIXME
sys.path.insert(0, str(Path(__file__).parent / "qrn/src/qrn" ))  #FIXME

from qrn import get_text, Index

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

MASTER_PASSWORD = "admin"  #FIXME
security = HTTPBasic()


def verify_password(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = "admin"
    is_correct_username = secrets.compare_digest(credentials.username, correct_username)
    is_correct_password = secrets.compare_digest(credentials.password, MASTER_PASSWORD)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, auth: bool = Depends(verify_password)):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/generate")
async def generate(
    ini_sura: int = 1,
    ini_verse: int = 1,
    ini_word: int = 1,
    ini_block: int = 1,

    end_sura: int = -1,
    end_verse: int = -1,
    end_word: int = -1,
    end_block: int = -1,

    get_archigraphemes: bool = False,
    get_blocks: bool = False,
    get_latin: bool = False,

    auth: bool = Depends(verify_password)
    ):

    try:
        result = get_text(
            source="tanzil-uthmani",
            ini_index=Index(
                sura=ini_sura,
                verse=ini_verse,
                word=ini_word,
                block=ini_block,
            ),
            end_index=Index(
                sura=end_sura,
                verse=end_verse,
                word=end_word,
                block=end_block,
            ),
            args={
                "blocks": get_blocks,
                "no_lat": not get_latin,
                "no_ara": get_latin,
                "no_graph": get_archigraphemes,
                "no_arch": not get_archigraphemes,
            }
        )
        return {"result": " ".join(res[0] for res in result)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

