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

from qrn import get_text


SURAS = [
    "ٱلْفَاتِحَة",
    "ٱلْبَقَرَة",
    "عِمْرَان",
    "ٱلنِّسَاء",
    "ٱلْمَائِدَة",
    "ٱلْأَنْعَام",
    "ٱلْأَعْرَاف",
    "ٱلْأَنْفَال",
    "ٱلتَّوْبَة",
    "يُونُس",
    "هُود",
    "يُوسُف",
    "ٱلرَّعْد",
    "إِبْرَاهِيم",
    "ٱلْحِجْر",
    "ٱلنَّحْل",
    "اٌلاِسْرٰاء",
    "ٱلْكَهْف",
    "مَرْيَم",
    "طه",
    "ٱلْأَنْبِيَاء",
    "ٱلْحَجّ",
    "ٱلْمُؤْمِنُون",
    "ٱلنُّور",
    "ٱلْفُرْقَان",
    "ٱلشُّعَرَاء",
    "ٱلنَّمْل",
    "ٱلْقَصَص",
    "ٱلْعَنْكَبُوت",
    "ٱلرُّوم",
    "لُقْمَان",
    "ٱلسَّجْدَة",
    "ٱلْأَحْزَاب",
    "سَبَأ",
    "فَاطِر",
    "يس",
    "ٱلصَّافَّات",
    "ص",
    "ٱلزُّمَر",
    "غَافِر",
    "فُصِّلَت",
    "ٱلشُّورىٰ",
    "ٱلْزُّخْرُف",
    "ٱلدُّخَان",
    "ٱلْجَاثِيَة",
    "ٱلْأَحْقَاف",
    "مُحَمَّد",
    "ٱلْفَتْح",
    "ٱلْحُجُرَات",
    "ق",
    "ٱلذَّارِيَات",
    "ٱلطُّور",
    "ٱلنَّجْم",
    "ٱلْقَمَر",
    "ٱلرَّحْمَٰن",
    "ٱلْوَاقِعَة",
    "ٱلْحَدِيد",
    "ٱلْمُجَادِلَة",
    "ٱلْحَشْر",
    "ٱلْمُمْتَحَنَة",
    "ٱلصَّفّ",
    "ٱلْجُمُعَة",
    "ٱلْمُنَافِقُون",
    "ٱلتَّغَابُن",
    "ٱلطَّلَاق",
    "ٱلتَّحْرِيم",
    "ٱلْمُلْك",
    "ٱلْقَلَم",
    "ٱلْحَاقَّة",
    "ٱلْمَعَارِج",
    "نُوح",
    "ٱلْجِنّ",
    "ٱلْمُزَّمِّل",
    "ٱلْمُدَّثِّر",
    "ٱلْقِيَامَة",
    "ٱلْإِنْسَان",
    "ٱلْمُرْسَلَات",
    "ٱلنَّبَأ",
    "ٱلنَّازِعَات",
    "عَبَسَ",
    "ٱلتَّكْوِير",
    "ٱلْإِنْفِطَار",
    "ٱلْمُطَفِّفِين",
    "ٱلْإِنْشِقَاق",
    "ٱلْبُرُوج",
    "ٱلطَّارِق",
    "ٱلْأَعْلَىٰ",
    "ٱلْغَاشِيَة",
    "ٱلْفَجْر",
    "ٱلْبَلَد",
    "ٱلشَّمْس",
    "ٱللَّيْل",
    "ٱلضُّحَىٰ",
    "ٱلشَّرْح",
    "ٱلتِّين",
    "ٱلْعَلَق",
    "ٱلْقَدْر",
    "ٱلْبَيِّنَة",
    "ٱلزَّلْزَلَة",
    "ٱلْعَادِيَات",
    "ٱلْقَارِعَة",
    "ٱلتَّكَاثُر",
    "ٱلْعَصْر",
    "ٱلْهُمَزَة",
    "ٱلْفِيل",
    "قُرَيْش",
    "ٱلْمَاعُون",
    "ٱلْكَوْثَر",
    "ٱلْكَافِرُون",
    "ٱلنَّصْر",
    "ٱلْمَسَد",
    "ٱلْإِخْلَاص",
    "ٱلْفَلَق",
    "ٱلنَّاس",
]

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
    show_verse_markers: bool = False,

    auth: bool = Depends(verify_password)

    ):

    try:
        result = get_text(
            source="tanzil-uthmani",
            ini_index=(ini_sura, ini_verse, ini_word, ini_block),
            end_index=(end_sura, end_verse, end_word, end_block),
            args={
                "blocks": get_blocks,
                "no_lat": not get_latin,
                "no_ara": get_latin,
                "no_graph": get_archigraphemes,
                "no_arch": not get_archigraphemes,
            }
        )

        if not show_verse_markers:
            content = " ".join(res[0] for res in result)
        else:
            text = []
            current_sura = None

            for key, tokens in groupby(result, key=lambda x: x[1].split(":")[:2]):
                sura, verse = key

                if not get_latin:
                    sura_header = f'﴿صُورِة {SURAS[int(sura)-1]}﴾\n'
                    sura = to_ara_num(sura)
                    verse = to_ara_num(verse)
                    verse_marker = f"۝{verse}"
                else:
                    sura_header = ""
                    verse_marker = f"{sura}:{verse}"

                verse_text = " ".join(t[0] for t in tokens)

                if current_sura != None:
                    sura_header = f"\n{sura_header}"

                if current_sura != sura:
                    text.append(sura_header)
                    current_sura = sura

                text.append(f"{verse_text} {verse_marker}")

            content = " ".join(text)

        return dict(result=content)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

