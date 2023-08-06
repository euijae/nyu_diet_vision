# Diet Vision

## Requirements

### PyTorch Model

This application requires `sam_vit_h_4b8939.pth` for image segmentation. The file is larger than 2.5 GB. Run the command below before running the application

```shell
python<version> config.py
```

This makes directory `/static/weights` and downloads the file into that folder.

## Run Application

To run the application, run the command below.

### Command

```shell
python main.py
```
