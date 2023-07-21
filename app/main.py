from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from .diet_vision import DietVision

app = FastAPI()   

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / "static"),
    name="static",
)

templates = Jinja2Templates(directory='templates')

app.dv_instance = None

def getInstance() -> DietVision:
    if app.dv_instance is None:
        app.dv_instance = DietVision()

    return app.dv_instance

@app.get('/test')
async def main(request: Request):
    return {'test1': 'test1 value'}

@app.get("/") 
async def main(request: Request):
    getInstance()

    return templates.TemplateResponse(
        "index.html", {"request": request}
    )

@app.get("/upload/image")
async def upload_image(request: Request):
    getInstance().upload_image()
    return {"message": "upload_image is successfully completed"}


@app.get('/segment/group/{x1}/{y1}/{x2}/{y2}')
async def group_segments(x1, y1, x2, y2):
    dv = getInstance()

    indices = dv.find_mask_indices([x1, y1, x2, y2])
    overlay_image_path = dv.create_overlay_image(indices)

    return {'path': overlay_image_path}


@app.get('/correct/class')
async def correct_image_class(request: Request):
    # TODO 
    return {'message': 'Hello World'}


@app.get('/segment/data/{x1}/{y1}/{x2}/{y2}')
async def get_object_data(x1: int, y1: int, x2: int, y2: int):
    dv = getInstance()
    
    indices = dv.find_mask_indices([x1, y1, x2, y2])
    overlay_image_path = dv.create_overlay_image(indices).split('/')[-1]
    obj_class, area = dv.get_data_by_mask_index(mask_index=indices[0])
    
    return {
        'class': obj_class, 
        'area': area, 
        'path': overlay_image_path
    }

@app.get('/clear')
async def clear_images(request: Request):
    app.dv_instance = None
    return {'message': 'Hello World'}

@app.get("/segment/data/test/{x1}/{y1}/{x2}/{y2}")
async def get_object_data2(x1: int, y1: int, x2: int, y2: int):
    return {
        'x1': x1, 'x2': x2, 'y2': y2, 'y1': y1
    }