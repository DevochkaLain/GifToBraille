from braille import Generator
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from io import BytesIO
import random

app = FastAPI()
braille_generator = Generator()
gif_list = {}


@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return html_content


@app.post("/upload-gif")
async def upload_gif(gif_file: UploadFile = File(...)):
    content = await gif_file.read()
    image_bytes = BytesIO(content)

    gif_id = random.randint(999999, 999999999)
    gif_list[gif_id] = {
        'image': image_bytes,
        'generator': None
    }

    return {'id': gif_id}


@app.post("/load_generator")
async def load_generator(gif_id: str = Form(...)):
    gif_id = int(gif_id)
    gif_data = gif_list[gif_id]

    gif_data['generator'] = braille_generator.gif_to_braille_image(gif_data['image'])

    return Response(status_code=200)


@app.post("/get-next-frame", response_class=PlainTextResponse)
async def get_next_frame(gif_id: str = Form(...)):
    try:
        gif_id = int(gif_id)
        generator = gif_list[gif_id]['generator']

    except:
        return 'Please Upload GIF!'

    try:
        braille_image = next(generator)

    except:
        braille_image = 'DONE'

        gif_list[gif_id]['generator'] = None

    return braille_image
