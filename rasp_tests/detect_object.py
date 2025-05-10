#!/usr/bin/python3

import os
import sys
import subprocess
import argparse
import time

def install_dependencies():
    print("Instalez dependențele necesare...")
    subprocess.run(["sudo", "apt", "update"], check=True)
    subprocess.run(["sudo", "apt", "install", "-y", "build-essential", "libatlas-base-dev", "python3-pip"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "tflite-runtime"], check=True)
    try:
        subprocess.run(["sudo", "apt", "install", "-y", "python3-opencv"], check=True)
    except subprocess.CalledProcessError:
        print("Instalez OpenCV din pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "opencv-python-headless"], check=True)
    print("Toate dependențele au fost instalate cu succes!")
    return True

def check_dependencies():
    missing_deps = []
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv")
    try:
        import tflite_runtime.interpreter
    except ImportError:
        missing_deps.append("tflite_runtime")
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    try:
        from picamera2 import Picamera2
    except ImportError:
        missing_deps.append("picamera2")
    if missing_deps:
        print(f"Următoarele dependențe lipsesc: {', '.join(missing_deps)}")
        choice = input("Doriți să le instalez acum? (d/n): ")
        if choice.lower() in ['d', 'da', 'y', 'yes']:
            install_dependencies()
            print("Dependențele au fost instalate. Reporniți scriptul.")
            sys.exit(0)
        else:
            print("Instalați dependențele manual și încercați din nou.")
            sys.exit(1)
    return True

if check_dependencies():
    import cv2
    import numpy as np
    import tflite_runtime.interpreter as tflite
    from picamera2 import MappedArray, Picamera2, Platform, Preview

normalSize = (1920, 1080)
lowresSize = (640, 640)

rectangles = []

start_time = time.time()
frame_count = 0
fps = 0

def ReadLabelFile(file_path):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        ret = {}
        first_line = lines[0].strip()
        has_index = len(first_line.split(maxsplit=1)) > 1 and first_line.split(maxsplit=1)[0].isdigit()
        for i, line in enumerate(lines):
            line = line.strip()
            if has_index:
                pair = line.split(maxsplit=1)
                if len(pair) == 2:
                    ret[int(pair[0])] = pair[1].strip()
            else:
                ret[i] = line
        return ret
    except FileNotFoundError:
        print(f"Eroare: Fișierul de etichete '{file_path}' nu a fost găsit.")
        sys.exit(1)
    except Exception as e:
        print(f"Eroare la citirea fișierului de etichete: {str(e)}")
        sys.exit(1)

def DrawRectangles(request):
    global fps
    with MappedArray(request, "main") as m:
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(m.array, f"FPS: {fps:.1f}", (50, 50), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
        for rect in rectangles:
            xmin, ymin, xmax, ymax = rect[0:4]
            cv2.rectangle(m.array, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            if len(rect) == 5:
                cv2.putText(m.array, rect[4], (xmin, ymin - 10), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

def classFilter(classdata):
    return [c.argmax() for c in classdata]

def YOLOdetect(output_data):
    output_data = output_data[0]
    boxes = np.squeeze(output_data[..., :4])
    scores = np.squeeze(output_data[..., 4:5])
    classes = classFilter(output_data[..., 5:])
    x, y, w, h = boxes[..., 0], boxes[..., 1], boxes[..., 2], boxes[..., 3]
    xyxy = [x - w / 2, y - h / 2, x + w / 2, y + h / 2]
    return xyxy, classes, scores

def download_model_files():
    models_dir = os.path.expanduser("~/models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "yolov5s-fp16.tflite")
    labels_path = os.path.join(models_dir, "coco_labels_yolov5.txt")
    if not os.path.exists(model_path):
        print(f"Descarc modelul YOLOv5s în {model_path}...")
        subprocess.run(["wget", "-O", model_path, "https://github.com/ultralytics/yolov5/releases/download/v6.0/yolov5s-fp16.tflite"], check=True)
    if not os.path.exists(labels_path):
        print(f"Descarc etichetele COCO în {labels_path}...")
        subprocess.run(["wget", "-O", labels_path, "https://raw.githubusercontent.com/ultralytics/yolov5/master/data/coco.names"], check=True)
    return model_path, labels_path

def main():
    global rectangles, start_time, frame_count, fps
    parser = argparse.ArgumentParser(description="Detecție obiecte YOLOv5 cu TensorFlow Lite pe Raspberry Pi")
    parser.add_argument('--model', help='Calea către modelul de detecție')
    parser.add_argument('--label', help='Calea către fișierul de etichete')
    parser.add_argument('--threshold', type=float, default=0.4, help='Prag de detecție (0.0-1.0)')
    parser.add_argument('--download', action='store_true', help='Descarcă automat modelul și etichetele')
    args = parser.parse_args()
    if args.download or (not args.model and not args.label):
        model_path, labels_path = download_model_files()
        args.model = model_path
        args.label = labels_path
    if not os.path.exists(args.model):
        print(f"Eroare: Fișierul model '{args.model}' nu a fost găsit.")
        sys.exit(1)
    if args.label:
        labels = ReadLabelFile(args.label)
    else:
        labels = None
    try:
        picam2 = Picamera2()
        picam2.start_preview(Preview.QTGL)
    except Exception as e:
        print(f"Eroare la inițializarea camerei: {str(e)}")
        print("Asigurați-vă că camera este conectată și activată în raspi-config")
        sys.exit(1)
    stream_format = "YUV420"
    if hasattr(Picamera2, 'platform') and Picamera2.platform == Platform.PISP:
        stream_format = "RGB888"
    config = picam2.create_preview_configuration(
        main={"size": normalSize},
        lores={"size": lowresSize, "format": stream_format}
    )
    picam2.configure(config)
    picam2.post_callback = DrawRectangles
    print("Pornesc camera...")
    picam2.start()
    print(f"Încarc modelul TensorFlow Lite: {args.model}")
    try:
        interpreter = tflite.Interpreter(model_path=args.model, num_threads=4)
        interpreter.allocate_tensors()
    except Exception as e:
        print(f"Eroare la încărcarea modelului: {str(e)}")
        sys.exit(1)
    print("Detecția obiectelor rulează. Apăsați Ctrl+C pentru a ieși.")
    try:
        while True:
            frame_start_time = time.time()
            img = picam2.capture_array("lores")
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            height = input_details[0]['shape'][1]
            width = input_details[0]['shape'][2]
            floating_model = False
            if input_details[0]['dtype'] == np.float32:
                floating_model = True
            if stream_format == "YUV420":
                img = cv2.cvtColor(img, cv2.COLOR_YUV420p2RGB)
            new_shape = (width, height)
            if new_shape != lowresSize:
                img = cv2.resize(img, new_shape)
            input_data = np.expand_dims(img, axis=0)
            if floating_model:
                input_data = (np.float32(input_data) - 127.5) / 127.5
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()
            output_data = interpreter.get_tensor(output_details[0]['index'])
            xyxy, classes, scores = YOLOdetect(output_data)
            rectangles = []
            for i in range(len(scores)):
                if ((scores[i] > args.threshold) and (scores[i] <= 1.0)):
                    xmin = int(max(1, (xyxy[0][i] * normalSize[0])))
                    ymin = int(max(1, (xyxy[1][i] * normalSize[1])))
                    xmax = int(min(normalSize[0], (xyxy[2][i] * normalSize[0])))
                    ymax = int(min(normalSize[1], (xyxy[3][i] * normalSize[1])))
                    box = [xmin, ymin, xmax, ymax]
                    rectangles.append(box)
                    if labels and classes[i] < len(labels):
                        rectangles[-1].append(labels[classes[i]])
            frame_count += 1
            if frame_count >= 10:
                end_time = time.time()
                fps = frame_count / (end_time - start_time)
                frame_count = 0
                start_time = time.time()
    except KeyboardInterrupt:
        print("\nÎnchid aplicația...")
    except Exception as e:
        print(f"Eroare: {str(e)}")
    finally:
        picam2.stop()
        print("Camera oprită.")

if __name__ == '__main__':
    main()