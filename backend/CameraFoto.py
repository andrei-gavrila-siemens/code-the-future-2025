import subprocess
import shlex
from PIL import Image
import CRNN

def take_photo(output, timout_ms,width,height):
    cmd= (f'libcamera-still -o {shlex.quote(output)} --timeout {timout_ms} -n --width {width} --height {height}')
    subprocess.run(cmd, shell=True, check=True)


def rotate(Photo):
    image = Image.open(Photo)
    rotated_image = image.rotate(180, expand=True)
    rotated_image.save("photo.jpg")

if __name__ == "__main__":
    take_photo("photo.jpg", 2000, 640, 640)
    rotate("photo.jpg")
    text = CRNN.imgToText('photo.jpg', langs=['ro', 'en'])
    print(text)