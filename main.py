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

MASTER_PASSWORD = "admin"
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
    ini_sura = int | None,
    ini_verse = int | None,
    ini_word = int | None,
    ini_block = int | None,

    end_sura = int | None,
    end_verse = int | None,
    end_word = int | None,
    end_block = int | None,

    get_archigraphemes = bool,
    get_blocks = bool,
    get_latin = bool,

    auth: bool = Depends(verify_password)):
    try:
        result = get_text(
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
                "no_graph": not get_archigraphemes,
                "no_arch": get_archigraphemes,
            }
        )
        result = list(result) #FIXME
        print(result) #FIXME
        return {"result": " ".join(res[0] for res in result)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

