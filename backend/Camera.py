import subprocess
import shlex

def take_photo(output, timout_ms,width,height):
    cmd= (f'libcamera-still -o {shlex.quote(output)} --timeout {timout_ms} -n --width {width} --height {height}')
    subprocess.run(cmd, shell=True, check=True)

if __name__ == "__main__":
    take_photo("test.jpg", 2000, 640, 480)