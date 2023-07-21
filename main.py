from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from diet_vision import DietVision

app = FastAPI()   

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / "static"),
    name="static",
)

templates = Jinja2Templates(directory='templates')

# TODO One instance of DietVision must be ready
dv_instance = None

def getInstance() -> DietVision:
    if dv_instance is None:
        dv_instance = DietVision()

    return dv_instance

@app.get("/") 
async def main(request: Request):
    getInstance()

    return templates.TemplateResponse(
        "index.html", {"request": request}
    )


@app.post("/upload/image")
async def upload_image(request: Request):
    getInstance().upload_image()
    return {"message": "Hello World"}


@app.get('/group/segments')
async def group_segments(request: Request):
    # TODO request sends x1, y1, x2, y2 OR x1 , y1
    # TODO iterate mask_dictionary and get a list of mask_index
    # TODO combine masks
    # TODO return the combined masks back to front
    return {'message': 'Hello World'}


@app.get('/correct/food_class')
async def correct_image_class(request: Request):
    # TODO 
    return {'message': 'Hello World'}


@app.get('/clear')
async def clear_images(request: Request):
    # TODO delete image from storage
    return {'message': 'Hello World'}