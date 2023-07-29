from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from .diet_vision import DietVision
from pydantic import BaseModel
import requests

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


@app.get("/upload/image")
async def upload_image(request: Request):
    getInstance().upload_image()
    return {"message": "upload_image is successfully completed"}


@app.post('/segment/group')
async def group_segments(bbox: BBox):
    x1, y1, x2, y2 = list(round_off([bbox.x1, bbox.y1, bbox.x2, bbox.y2]))
    indices = getInstance().find_mask_index_list(list(round_off([x1, y1, x2, y2])), True)
    # indices = getInstance().update_mask_index_list(indices)
    overlay_image_path = getInstance().create_overlay_image(indices).split('/')[-1]

    return {'path': overlay_image_path}


@app.post('/segment/data')
async def get_object_data(bbox: BBox):
    x1, y1, x2, y2 = list(round_off([bbox.x1, bbox.y1, bbox.x2, bbox.y2]))    
    indices = getInstance().find_mask_index_list(list(round_off([x1, y1, x2, y2])))
    indices = getInstance().expand_mask_index_list(indices)

    overlay_image_path = getInstance().create_overlay_image(indices).split('/')[-1]
    obj_class, area = getInstance().get_data_by_mask_index(mask_index=indices[0])
    calories = get_nutrition_info(obj_class)
    
    return {
        'class': obj_class, 
        'volume': area, 
        'path': overlay_image_path,
        'calories': calories
    }


@app.post('/classify/modify')
async def correct_food_class(fc: FoodClass):
    getInstance().correct_food_class(fc.food_class)

    return {'updated_food_class': fc.food_class }


@app.get('/clear')
async def clear_images(request: Request):
    app.dv_instance = None
    return {'message': 'Hello World'}

def get_nutrition_info(food_name):
    food_name = food_name.replace('_', ' ')

    #Make request to Nutritionix API
    response = requests.get(
        "https://trackapi.nutritionix.com/v2/search/instant",
        params={"query": food_name},
        headers={
            "x-app-id": "a3663db3",
            "x-app-key": "06eee2ab6e395eb02e4500d70f0fcdee"
        }
    )
    #Parse response and return relevant information
    data = response.json()
    response = data["branded"][0]["photo"]["thumb"]
    return {
        "food_name": data["branded"][0]["food_name"],
        "calories": data["branded"][0]["nf_calories"],
        "serving_size": data["branded"][0]["serving_qty"],
        "serving_unit": data["branded"][0]["serving_unit"]
    }