import json
import random
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class JsonChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
    
    def on_modified(self, event):
        if event.src_path.endswith('object_detections.json'):
            self.callback()

def are_substances_different(new_data, existing_file):
    if not os.path.exists(existing_file):
        return True
    
    try:
        with open(existing_file, 'r') as f:
            old_data = json.load(f)
        
        
        old_substances = sorted(old_data.get('substances', []), key=lambda x: (x['x0'], x['y0']))
        new_substances = sorted(new_data.get('substances', []), key=lambda x: (x['x0'], x['y0']))
        
        if len(old_substances) != len(new_substances):
            return True
            
        for old_sub, new_sub in zip(old_substances, new_substances):
            if (old_sub['color'] != new_sub['color'] or
                old_sub['count'] != new_sub['count'] or
                old_sub['x0'] != new_sub['x0'] or
                old_sub['xf'] != new_sub['xf'] or
                old_sub['y0'] != new_sub['y0'] or
                old_sub['yf'] != new_sub['yf']):
                return True
                
        return False
        
    except (json.JSONDecodeError, KeyError):
        return True

def process_object_detections():
    try:
        input_file = 'object_detections.json'
        output_file = 'substances.json'
        
        with open(input_file, 'r') as f:
            object_data = json.load(f)
        
        output_data = {
            "seed": random.randint(1, 100),
            "substances": []
        }
        
        for detection in object_data:
            
            area = detection["area_pixels"]
            if 100000 <= area <= 200000:
                count = area // 1000
            else:
                count = area // 10000
            
            count = max(50, min(count, 200))
            
            x0 = detection["dist_to_left_margin_pixels"]
            xf = x0 + detection["width_pixels"]
            y0 = detection["dist_to_top_margin_pixels"]
            yf = y0 + detection["height_pixels"]
            
            color = random.randint(1, 7)
            
            output_data['substances'].append({
                "color": color,
                "count": count,
                "x0": x0,
                "xf": xf,
                "y0": y0,
                "yf": yf
            })
        
        
        if are_substances_different(output_data, output_file):
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - New data detected. Updated {output_file}")
        else:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - No substantial changes detected.")
    
    except FileNotFoundError:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Error: Input file {input_file} not found.")
    except json.JSONDecodeError:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Error: Could not parse {input_file}. Invalid JSON format.")
    except KeyError as e:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Error: Missing expected key in detection data: {str(e)}")
    except Exception as e:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - An unexpected error occurred: {str(e)}")

def start_watching():
    # Run initial processing
    process_object_detections()
    
    # Set up file watcher
    event_handler = JsonChangeHandler(process_object_detections)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Watching for changes to object_detections.json...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    try:
        from watchdog.observers import Observer
    except ImportError:
        print("Installing watchdog package...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'watchdog'])
    
    start_watching()
