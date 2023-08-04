from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from .diet_vision import DietVision
from pydantic import BaseModel
import requests, os, base64

class BBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class FoodClass(BaseModel):
    food_class: str

app = FastAPI()   

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / "static"),
    name="static",
)

origins = [
    "http://http://127.0.0.1/",
    "http://127.0.0.1/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.dv_instance = None

templates = Jinja2Templates(directory='templates')
round_off = lambda x: map(lambda f : round(float(f)), x)

def getInstance() -> DietVision:
    if app.dv_instance is None:
        app.dv_instance = DietVision()

    return app.dv_instance


@app.get("/") 
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post('/segment/group')
async def group_segments(bbox: BBox):
    try:
        bbox_plot = list(round_off([bbox.x1, bbox.y1, bbox.x2, bbox.y2]))
        indices = getInstance().find_mask_index_list(bbox_plot, True)

        if not indices:
            return {'file_name': getInstance().blank_transparent_image_path}

        overlay_image_path = getInstance().create_overlay_image(False, indices)
        overlay_image_name = overlay_image_path.split('/')[-1]

        return {'file_name': overlay_image_name}

    except Exception as ex:
        return {'error_message': ex}


@app.post('/segment/data')
async def get_object_data(bbox: BBox):
    try:
        bbox_plot = list(round_off([bbox.x1, bbox.y1, bbox.x2, bbox.y2])) 
        indices = getInstance().find_mask_index_list(bbox_plot, False)

        if not indices:
            return {"class": "n/a (The pixel doesn't belong to any objects)", 'volume': 0 }

        obj_class, area = getInstance().get_data_by_mask_index(mask_index=indices[0])
        
        return { 'class': obj_class, 'volume': area }
    
    except Exception as ex:
        return {'error_message': ex}


@app.post('/classify/modify')
async def update_food_class(fc: FoodClass):
    try:
        getInstance().update_food_class(fc.food_class)
        overlay_image_path = getInstance().create_overlay_image(True)
        file_name = overlay_image_path.split('/')[-1]

        return { 'updated_food_class': fc.food_class, 'file_name': file_name }

    except Exception as ex:
        return {'error_message': ex}


@app.get('/clear')
async def clear_images(request: Request):
    app.dv_instance = None
    return {'message': 'Successfully cleared the DietVision'}


@app.post('/upload/image')
async def save_image(filename: str = Form(...), filedata: str = Form(...)):    
    # Pass
    try:
        static_directory = getInstance().HOME
        file_location = os.path.join(static_directory, 'images', filename)

        image_as_bytes = str.encode(filedata)
        img_recovered = base64.b64decode(image_as_bytes)

        with open(file_location, 'wb') as f:
            f.write(img_recovered)
            overlay_image_path = getInstance().upload_image(filename)
            overlay_image_name = overlay_image_path.split('/')[-1]

            return { "file_name": overlay_image_name }

    except Exception as ex:
        return {'error_message': ex}
