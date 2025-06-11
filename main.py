from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from itertools import groupby
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
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, auth: bool = Depends(verify_password)):
    return templates.TemplateResponse("index.html", {"request": request})


def to_ara_num(
    text_num: str,
    numbers: list[str] = ["٠", "١", "٢", "٣", "٤", "٥", "٦", "٧", "٨", "٩"]
    ):
    """
    Convert numbers into Arabic numbers
    """
    return "".join(numbers[int(t)] for t in text_num)


@app.get("/extract")
async def extract(
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
    hide_verse_markers: bool = False,

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

        if hide_verse_markers:
            return {"result": " ".join(res[0] for res in result)}
        else:
            text = []
            current_sura = None

            for key, tokens in groupby(result, key=lambda x: x[1].split(":")[:2]):
                sura, verse = key

                if not get_latin:
                    sura = to_ara_num(sura)
                    verse = to_ara_num(verse)
                    sura_header = f"﴿ صوره {sura} ﴾"
                    verse_marker = f"۝{verse}"
                else:
                    sura_header = ""
                    verse_marker = f"{sura}:{verse}"

                verse_text = " ".join(t[0] for t in tokens)

                if current_sura != sura:
                    text.append(sura_header)
                    current_sura = sura

                text.append(f"{verse_text} {verse_marker}")

            return {"result": " ".join(text)}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

