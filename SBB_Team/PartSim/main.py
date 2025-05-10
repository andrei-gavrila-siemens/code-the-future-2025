import pygame
import math
import numpy as np
import random
import json
import os


MAX_RADIUS = 200
MAX_CLUSTERS = 20
MIN_CLUSTER_SIZE = 50
PREDEFINED_COLORS = [(0, 255, 0), (255, 0, 0), (255, 165, 0), (0, 255, 255), (255, 0, 255), (230, 230, 250), (0, 128, 128)]  # RGB tuples
SETTINGS = {
    'seed': 12,
    'atoms': {
        'count': 150,  # per color
        'radius': 1,
    },
    'drawings': {
        'lines': False,
        'circle': False,
        'clusters': False,
        'background_color': (0, 0, 0),
    },
    'numColors': 7,
    'time_scale': 1.0,
    'viscosity': 0.7,
    'gravity': 0.0,
    'wallRepel': 40,
    'rules': {},
    'radii': {},
    'colors': [],
    'color_map': {},
    'rulesArray': [],
    'radii2Array': [],
    'color_to_index': {},  # map color values to indices
    'yes': False
}


pygame.init()
width, height = 1000, 500
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption(f"Life #{SETTINGS['seed']}")



atoms = []
clusters = []
total_v = 0.0
local_seed = SETTINGS['seed']
selected_cluster_color = None
cluster_offsets = []



def mulberry32():
    global local_seed
    t = local_seed = (local_seed + 0x6D2B79F5) & 0xFFFFFFFF
    t = (t ^ (t >> 15)) * (t | 1) & 0xFFFFFFFF
    t ^= (t + ((t ^ (t >> 7)) * (t | 61))) & 0xFFFFFFFF
    return ((t ^ (t >> 14)) >> 0) / 4294967296.0


def random_rules():
    global local_seed
    if not isinstance(SETTINGS['seed'], (int, float)):
        SETTINGS['seed'] = 0xcafecafe
    local_seed = SETTINGS['seed']
    print(f"Seed={local_seed}")
    SETTINGS['rules'] = {}
    SETTINGS['color_to_index'] = {c: i for i, c in enumerate(SETTINGS['colors'])}
    for i in SETTINGS['colors']:
        SETTINGS['rules'][i] = {}
        for j in SETTINGS['colors']:
            SETTINGS['rules'][i][j] = mulberry32() * 2 - 1
        SETTINGS['radii'][i] = 80
    flatten_rules()


def flatten_rules():
    SETTINGS['rulesArray'] = []
    SETTINGS['radii2Array'] = []
    for c1 in SETTINGS['colors']:
        for c2 in SETTINGS['colors']:
            SETTINGS['rulesArray'].append(SETTINGS['rules'][c1][c2])
        SETTINGS['radii2Array'].append(SETTINGS['radii'][c1] * SETTINGS['radii'][c1])


def set_number_of_colors():
    SETTINGS['colors'] = list(range(SETTINGS['numColors']))
    SETTINGS['color_map'] = {i: PREDEFINED_COLORS[i % len(PREDEFINED_COLORS)] for i in range(SETTINGS['numColors'])}
    SETTINGS['color_to_index'] = {c: i for i, c in enumerate(SETTINGS['colors'])}


def random_x(x0, xf):
    return random.uniform(x0, xf)

def random_y(y0, yf):
    return random.uniform(y0, yf)



def create(number, color, x0, xf, y0, yf):
    return [[random_x(x0, xf), random_y(y0, yf), 0, 0, color] for _ in range(number)]



def reset_simulation():
    global atoms, clusters, local_seed, SETTINGS, total_v, selected_cluster_color, cluster_offsets
    atoms = []
    clusters = []
    total_v = 0.0
    selected_cluster_color = None
    cluster_offsets = []
    SETTINGS.update({
        'rules': {},
        'radii': {},
        'rulesArray': [],
        'radii2Array': [],
        'colors': [],
        'color_map': {},
        'color_to_index': {},
        'numColors': 0,
        'seed': 12,
    })
    local_seed = SETTINGS['seed']



def validate_substance(s):
    required_keys = ['count', 'color', 'x0', 'xf', 'y0', 'yf']
    if not all(key in s for key in required_keys):
        return False
    if not all(isinstance(s[key], (int, float)) for key in required_keys):
        return False
    if not isinstance(s['color'], int) or s['color'] < 0:
        print(f"Warning: Invalid color value {s['color']} in substance. Must be a non-negative integer.")
        return False
    if s['color'] >= len(PREDEFINED_COLORS):
        print(f"Warning: Color value {s['color']} exceeds available colors ({len(PREDEFINED_COLORS)}). Using modulo mapping.")
    return True



def update_atoms(filename, clear_previous):
    global atoms, local_seed
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading {filename}: {e}")
        return

    substances = data.get('substances', [])
    if not substances:
        print("No substances found in JSON")
        return
    if not all(validate_substance(s) for s in substances):
        print("Invalid substance data in JSON")
        return

    if clear_previous:
        reset_simulation()

    SETTINGS['numColors'] = len(substances)
    SETTINGS['colors'] = [s['color'] for s in substances]
    SETTINGS['color_map'] = {i: PREDEFINED_COLORS[i % len(PREDEFINED_COLORS)] for i in SETTINGS['colors']}

    if 'seed' in data:
        SETTINGS['seed'] = data['seed']
        local_seed = SETTINGS['seed']

    random_rules()

    for s in substances:
        atoms.extend(create(
            s['count'], s['color'],
            s['x0'], s['xf'],
            s['y0'], s['yf']
        ))

    print(f"Simulation restarted with {len(atoms)} atoms")

def draw_square(surface, x, y, color, radius):
    pygame.draw.rect(surface, color, (x - radius, y - radius, 2 * radius, 2 * radius))

def draw_circle(surface, x, y, color, radius, fill=True):
    pygame.draw.circle(surface, color, (x, y), radius, 0 if fill else 1)

def draw_line_between_atoms(surface, ax, ay, bx, by, color):
    pygame.draw.line(surface, color, (ax, ay), (bx, by))


def apply_rules():
    global total_v
    total_v = 0.0
    forces = []
    mouse_pos = pygame.mouse.get_pos() if selected_cluster_color is not None else None

    for a in atoms:
        if a[4] not in SETTINGS['color_to_index']:
            print(f"Warning: Atom with invalid color {a[4]}")
            continue
        
        
        if selected_cluster_color is not None and a[4] == selected_cluster_color:
            forces.append((0, 0))
            continue

        fx = 0
        fy = 0
        idx = SETTINGS['color_to_index'][a[4]] * SETTINGS['numColors']
        r2 = SETTINGS['radii2Array'][SETTINGS['color_to_index'][a[4]]] if SETTINGS['color_to_index'][a[4]] < len(SETTINGS['radii2Array']) else 80 * 80
        for b in atoms:
            if b[4] not in SETTINGS['color_to_index']:
                print(f"Warning: Atom with invalid color {b[4]}")
                continue
            b_idx = SETTINGS['color_to_index'][b[4]]
            rule_idx = idx + b_idx
            if rule_idx < len(SETTINGS['rulesArray']):
                g = SETTINGS['rulesArray'][rule_idx]
            else:
                g = 0
                try:
                    print(f"Warning: Invalid rule index {rule_idx} for colors {a[4]} and {b[4]}")
                except Exception as e:
                    print(f"Error printing warning: {e}")
            dx = a[0] - b[0]
            dy = a[1] - b[1]
            if dx != 0 or dy != 0:
                d = dx * dx + dy * dy
                if d < r2:
                    F = g / math.sqrt(d)
                    fx += F * dx
                    fy += F * dy
                    if SETTINGS['drawings']['lines']:
                        color = SETTINGS['color_map'].get(b[4], (255, 255, 255))  # Fallback to white
                        draw_line_between_atoms(screen, a[0], a[1], b[0], b[1], color)
        if SETTINGS['wallRepel'] > 0:
            d = SETTINGS['wallRepel']
            strength = 0.1
            if a[0] < d:
                fx += (d - a[0]) * strength
            if a[0] > width - d:
                fx += (width - d - a[0]) * strength
            if a[1] < d:
                fy += (d - a[1]) * strength
            if a[1] > height - d:
                fy += (height - d - a[1]) * strength
        fy += SETTINGS['gravity']
        forces.append((fx, fy))

    for a, (fx, fy) in zip(atoms, forces):
        if selected_cluster_color is None or a[4] != selected_cluster_color:
            vmix = 1.0 - SETTINGS['viscosity']
            a[2] = a[2] * vmix + fx * SETTINGS['time_scale']
            a[3] = a[3] * vmix + fy * SETTINGS['time_scale']
            total_v += abs(a[2]) + abs(a[3])

            a[0] += a[2]
            a[1] += a[3]

            if a[0] < 0:
                a[0] = -a[0]
                a[2] *= -1
            if a[0] >= width:
                a[0] = 2 * width - a[0]
                a[2] *= -1
            if a[1] < 0:
                a[1] = -a[1]
                a[3] *= -1
            if a[1] >= height:
                a[1] = 2 * height - a[1]
                a[3] *= -1
    total_v /= len(atoms) if atoms else 1


json_file = './substances.json'
try:
    update_atoms(json_file, True)
    last_mtime = os.path.getmtime(json_file)
except OSError as e:
    print(f"Error accessing {json_file}: {e}")
    last_mtime = 0

file_check_interval = 60
frame_count = 0
clock = pygame.time.Clock()
running = True
mouse_held = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            width, height = event.size
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_held = True
                mouse_x, mouse_y = event.pos
                
                min_dist = float('inf')
                closest_atom = None
                for a in atoms:
                    dist = math.hypot(a[0] - mouse_x, a[1] - mouse_y)
                    if dist < min_dist and dist < 50:
                        min_dist = dist
                        closest_atom = a
                if closest_atom:
                    selected_cluster_color = closest_atom[4]
                    cluster_offsets = [(a[0] - mouse_x, a[1] - mouse_y) for a in atoms if a[4] == selected_cluster_color]
                    print(f"Selected cluster with color {selected_cluster_color}")
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_held = False
                selected_cluster_color = None
                cluster_offsets = []
                print("Deselected cluster")

    frame_count += 1
    if frame_count >= file_check_interval:
        try:
            current_mtime = os.path.getmtime(json_file)
            if current_mtime != last_mtime:
                print("Changes detected in particle.json")
                update_atoms(json_file, clear_previous=True)
                last_mtime = current_mtime
        except OSError as e:
            print(f"Error checking file {json_file}: {e}")
        frame_count = 0

    
    if mouse_held and selected_cluster_color is not None:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        i = 0
        for a in atoms:
            if a[4] == selected_cluster_color:
                if i < len(cluster_offsets):
                    a[0] = mouse_x + cluster_offsets[i][0]
                    a[1] = mouse_y + cluster_offsets[i][1]
                    a[2] = 0
                    a[3] = 0
                    i += 1

    screen.fill(SETTINGS['drawings']['background_color'])
    apply_rules()

    for a in atoms:
        color = SETTINGS['color_map'].get(a[4], (255, 255, 255))
        try:
            if SETTINGS['drawings']['circle']:
                draw_circle(screen, a[0], a[1], color, SETTINGS['atoms']['radius'])
            else:
                draw_square(screen, a[0], a[1], color, SETTINGS['atoms']['radius'])
        except Exception as e:
            print(f"Error drawing atom with color {a[4]}: {e}")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
