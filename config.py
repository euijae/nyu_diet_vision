import os
import glob


CURRENT_DIRECTORY = os.getcwd()
MODEL_PTY_DIRECTORY = os.path.join(CURRENT_DIRECTORY, 'static', 'weights')
MODEL_PTY_FILE = os.path.join(MODEL_PTY_DIRECTORY, 'sam_vit_h_4b8939.pth')

if not os.path.exists(MODEL_PTY_DIRECTORY):
    os.mkdir(MODEL_PTY_DIRECTORY)

if not os.path.exists(MODEL_PTY_FILE):
    os.system('wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth')