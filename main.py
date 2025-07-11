
# Copyright (c) 2025 Alicia González Martínez

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic_settings import BaseSettings
from passlib.context import CryptContext
from itertools import groupby
import secrets

from qran import get_text


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


class Settings(BaseSettings):
    ADMIN_USERNAME: str
    ADMIN_PASSWORD_HASH: str
    USER1_USERNAME: str
    USER1_PASSWORD_HASH: str
    USER2_USERNAME: str
    USER2_PASSWORD_HASH: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # ignore extra env vars

settings = Settings()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


templates = Jinja2Templates(directory="templates")


security = HTTPBasic(auto_error=True)


users_db = {
    "guest": pwd_context.hash("guest"),
    settings.ADMIN_USERNAME: settings.ADMIN_PASSWORD_HASH,
    settings.USER1_USERNAME: settings.USER1_PASSWORD_HASH,
    settings.USER2_USERNAME: settings.USER2_PASSWORD_HASH,
}


async def verify_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    if not credentials:
        return ""
    stored_hash = users_db.get(credentials.username)
    if not stored_hash or not pwd_context.verify(credentials.password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
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
    username: str = Depends(verify_user)
    ):

    alert = None
    if not username or username == "guest":
        ini_sura = end_sura = 3
        alert = "You are not authenticated. Showing results for Surah 3 only."

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

                if current_sura is not None:
                    sura_header = f"\n{sura_header}"

                if current_sura != sura:
                    text.append(sura_header)
                    current_sura = sura

                text.append(f"{verse_text} {verse_marker}")

            content = " ".join(text)

        return dict(result=content, alert=alert)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

