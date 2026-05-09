# """
# modules/tts.py
#
# Модуль синтезу мовлення (Text-to-Speech) для музейного гіда.
# Перетворює текстовий опис експоната на аудіофайл .mp3 через gTTS.
# """
#
# import uuid
# from pathlib import Path
#
# from gtts import gTTS
#
# # ---------------------------------------------------------------------------
# # Конфігурація
# # ---------------------------------------------------------------------------
#
# OUTPUT_DIR = Path("outputs")
# OUTPUT_DIR.mkdir(exist_ok=True)
#
# DEFAULT_LANG = "uk"  # українська
#
#
# # ---------------------------------------------------------------------------
# # Основна функція
# # ---------------------------------------------------------------------------
#
# def text_to_speech(text: str, lang: str = DEFAULT_LANG) -> Path:
#     """
#     Генерує аудіофайл із тексту.
#
#     Args:
#         text: текст для озвучування
#         lang:  мовний код ('uk' — українська, 'en' — англійська)
#
#     Returns:
#         Path до згенерованого .mp3 файлу
#
#     Raises:
#         RuntimeError: якщо gTTS повернув помилку
#     """
#     if not text or not text.strip():
#         raise ValueError("Текст для озвучування не може бути порожнім")
#
#     output_path = OUTPUT_DIR / f"audio_{uuid.uuid4().hex[:8]}.mp3"
#
#     try:
#         tts = gTTS(text=text.strip(), lang=lang, slow=False)
#         tts.save(str(output_path))
#     except Exception as e:
#         raise RuntimeError(f"gTTS error: {e}") from e
#
#     return output_path
#
#
# # ---------------------------------------------------------------------------
# # Утиліта: очистити старі файли з outputs/
# # ---------------------------------------------------------------------------
#
# def cleanup_old_audio(keep_last: int = 5) -> None:
#     """Видаляє старі mp3 файли, залишає тільки keep_last останніх."""
#     files = sorted(OUTPUT_DIR.glob("audio_*.mp3"), key=lambda f: f.stat().st_mtime)
#     for old_file in files[:-keep_last]:
#         old_file.unlink(missing_ok=True)
#
#
# if __name__ == "__main__":
#     test_text = (
#         "Мона Ліза. Автор: Леонардо да Вінчі. "
#         "Написана між 1503 та 1519 роками. "
#         "Картина зберігається в Луврі в Парижі і є найвідомішим твором мистецтва у світі."
#     )
#
#     path = text_to_speech(test_text)
#     print(f"✅ Аудіо збережено: {path}")

"""
modules/tts.py

Модуль синтезу мовлення (Text-to-Speech) для музейного гіда.
Використовує Edge TTS (Microsoft) — безкоштовно, без ключа.
Голос: uk-UA-PolinaNeural
"""

import asyncio
import uuid
from pathlib import Path

import edge_tts

# ---------------------------------------------------------------------------
# Конфігурація
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

VOICE_UK = "uk-UA-PolinaNeural"
VOICE_EN = "en-US-JennyNeural"


# ---------------------------------------------------------------------------
# Основна функція
# ---------------------------------------------------------------------------

def text_to_speech(text: str, lang: str = "uk") -> Path:
    """
    Генерує аудіофайл із тексту через Edge TTS.

    Args:
        text: текст для озвучування
        lang: 'uk' — українська, 'en' — англійська

    Returns:
        Path до згенерованого .mp3 файлу
    """
    if not text or not text.strip():
        raise ValueError("Текст для озвучування не може бути порожнім")

    voice = VOICE_UK if lang == "uk" else VOICE_EN
    output_path = OUTPUT_DIR / f"audio_{uuid.uuid4().hex[:8]}.mp3"

    asyncio.run(_generate(text.strip(), voice, output_path))
    return output_path


async def _generate(text: str, voice: str, output_path: Path) -> None:
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(str(output_path))


# ---------------------------------------------------------------------------
# Утиліта: очистити старі файли з outputs/
# ---------------------------------------------------------------------------

def cleanup_old_audio(keep_last: int = 5) -> None:
    """Видаляє старі mp3 файли, залишає тільки keep_last останніх."""
    files = sorted(OUTPUT_DIR.glob("audio_*.mp3"), key=lambda f: f.stat().st_mtime)
    for old_file in files[:-keep_last]:
        old_file.unlink(missing_ok=True)


if __name__ == "__main__":
    test_text = (
        "Мона Ліза. Автор: Леонардо да Вінчі. "
        "Написана між 1503 та 1519 роками. "
        "Картина зберігається в Луврі в Парижі і є найвідомішим твором мистецтва у світі."
    )

    path = text_to_speech(test_text)
    print(f"✅ Аудіо збережено: {path}")