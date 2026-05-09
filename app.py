"""
app.py — MuseGuide AI
Gradio-інтерфейс для розпізнавання музейних експонатів і картин.
"""

import gradio as gr
from PIL import Image

from modules.llm import analyze_exhibit, format_for_tts, NotAnExhibitError
from modules.tts import text_to_speech, cleanup_old_audio

# ---------------------------------------------------------------------------
# Кастомна тема та CSS
# ---------------------------------------------------------------------------

custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500&display=swap');

:root {
    --museum-gold: #C9A84C;
    --museum-dark: #1a1a1a;
    --museum-cream: #F5F0E8;
    --museum-stone: #8B7355;
    --museum-card: #FDFAF4;
}

body, .gradio-container {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--museum-cream) !important;
}

/* Заголовок */
.museum-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    border-bottom: 1px solid #D4C5A9;
    margin-bottom: 1.5rem;
}
.museum-header h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 2.6rem !important;
    font-weight: 600 !important;
    color: var(--museum-dark) !important;
    letter-spacing: 0.02em;
    margin: 0 !important;
}
.museum-header p {
    font-size: 0.95rem;
    color: var(--museum-stone);
    margin-top: 0.4rem;
    font-weight: 300;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Секції результату */
.result-card {
    background: var(--museum-card) !important;
    border: 1px solid #D4C5A9 !important;
    border-radius: 4px !important;
    padding: 1.2rem 1.4rem !important;
    margin-bottom: 0.8rem !important;
}
.result-card label {
    font-family: 'Playfair Display', serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: var(--museum-gold) !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
}

/* Кнопка */
.analyze-btn {
    background: var(--museum-dark) !important;
    color: #F5F0E8 !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    padding: 0.85rem 2rem !important;
    width: 100% !important;
    transition: background 0.2s ease !important;
}
.analyze-btn:hover {
    background: var(--museum-stone) !important;
}

/* Upload зона */
.upload-zone {
    border: 1.5px dashed #C9A84C !important;
    border-radius: 4px !important;
    background: #FDFAF4 !important;
}

/* Розділювач */
.divider {
    border: none;
    border-top: 1px solid #D4C5A9;
    margin: 1rem 0;
}

/* Факти — окремі чіпи */
.facts-box textarea {
    font-size: 0.9rem !important;
    line-height: 1.8 !important;
    color: var(--museum-dark) !important;
}

/* Аудіо */
audio {
    width: 100% !important;
    border-radius: 4px !important;
}

/* Приховати footer Gradio */
footer { display: none !important; }
"""

# ---------------------------------------------------------------------------
# Логіка обробки
# ---------------------------------------------------------------------------

def process_image(image: Image.Image):
    if image is None:
        return ("", "", "", "", "", "", "", None)

    try:
        data = analyze_exhibit(image)
    except NotAnExhibitError as e:
        raise gr.Error(str(e))

    cleanup_old_audio()
    audio_path = text_to_speech(format_for_tts(data))

    facts = "\n".join(f"• {f}" for f in data.get("цікаві_факти", []))

    return (
        data.get("назва", ""),
        f"{data.get('автор_або_культура', '')}  ·  {data.get('період', '')}",
        data.get("тип_експоната", "").capitalize(),
        data.get("матеріал_або_техніка", ""),
        data.get("де_зберігається", ""),
        facts,
        data.get("екскурсійний_опис", ""),
        str(audio_path),
    )

# ---------------------------------------------------------------------------
# Інтерфейс
# ---------------------------------------------------------------------------

with gr.Blocks(title="MuseGuide AI") as demo:

    # Заголовок
    gr.HTML("""
        <div class="museum-header">
            <h1>🏛 MuseGuide AI</h1>
            <p>Інтелектуальний музейний гід · Розпізнавання експонатів</p>
        </div>
    """)

    with gr.Row():
        # Ліва колонка — завантаження
        with gr.Column(scale=1):
            image_input = gr.Image(
                type="pil",
                label="Фото експоната або картини",
                elem_classes=["upload-zone"],
                height=340,
            )
            analyze_btn = gr.Button(
                "Розпізнати експонат",
                elem_classes=["analyze-btn"],
                variant="primary",
            )

        # Права колонка — результат
        with gr.Column(scale=1):
            out_title = gr.Textbox(
                label="Назва",
                interactive=False,
                elem_classes=["result-card"],
                lines=1,
            )
            out_author = gr.Textbox(
                label="Автор · Період",
                interactive=False,
                elem_classes=["result-card"],
                lines=1,
            )
            with gr.Row():
                out_type = gr.Textbox(
                    label="Тип",
                    interactive=False,
                    elem_classes=["result-card"],
                    lines=1,
                )
                out_material = gr.Textbox(
                    label="Матеріал / техніка",
                    interactive=False,
                    elem_classes=["result-card"],
                    lines=1,
                )
            out_location = gr.Textbox(
                label="Де зберігається",
                interactive=False,
                elem_classes=["result-card"],
                lines=1,
            )
            out_facts = gr.Textbox(
                label="Цікаві факти",
                interactive=False,
                elem_classes=["result-card", "facts-box"],
                lines=4,
            )
            out_description = gr.Textbox(
                label="Екскурсовод",
                interactive=False,
                elem_classes=["result-card"],
                lines=3,
            )
            out_audio = gr.Audio(
                label="Аудіосупровід",
                type="filepath",
                autoplay=True,
            )

    # Прив'язка
    analyze_btn.click(
        fn=process_image,
        inputs=image_input,
        outputs=[
            out_title,
            out_author,
            out_type,
            out_material,
            out_location,
            out_facts,
            out_description,
            out_audio,
        ],
    )

if __name__ == "__main__":
    demo.launch(css=custom_css)