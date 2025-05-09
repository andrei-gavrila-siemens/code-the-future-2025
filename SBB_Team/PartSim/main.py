import pygame
import math
import numpy as np
import random


MAX_RADIUS = 200
MAX_CLUSTERS = 20
MIN_CLUSTER_SIZE = 50
PREDEFINED_COLORS = [(0, 255, 0), (255, 0, 0), (255, 165, 0), (0, 255, 255), (255, 0, 255), (230, 230, 250), (0, 128, 128)]  # RGB tuples
SETTINGS = {
    'seed': 12, #91651088029
    'atoms': {
        'count': 150,  # Per color
        'radius': 1,
    },
    'drawings': {
        'lines': False,
        'circle': False,
        'clusters': False,
        'background_color': (0, 0, 0),
    },
    'numColors': 4,
    'time_scale': 1.0,
    'viscosity': 0.7,
    'gravity': 0.0,
    'wallRepel': 40,
    'rules': {},
    'radii': {},
    'colors': [],
    'yes': False
}

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
#width, height = screen.get_size()
#width = int(width * 0.9)
#height = int(height * 0.9)
width, height = 1000, 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption(f"Life #{SETTINGS['seed']}")

# deterministic randomosity
local_seed = SETTINGS['seed']

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
    
    SETTINGS['color_map'] = {i: PREDEFINED_COLORS[i] for i in range(SETTINGS['numColors'])}


def random_x(x0, xf):
    return random.uniform(x0, xf)

def random_y(y0, yf):
    return random.uniform(y0, yf)


def create(number, color, x0, xf, y0, yf):
    return [[random_x(x0, xf), random_y(y0, yf), 0, 0, color] for _ in range(number)]

def place_atoms(number_of_atoms_per_color, clear_previous):
    global atoms
    if clear_previous:
        atoms = []

    subst = int(input("Number of substances: "))
    SETTINGS['numColors'] = subst
    SETTINGS['colors'] = list(range(subst))
    SETTINGS['color_map'] = {i: PREDEFINED_COLORS[i % len(PREDEFINED_COLORS)] for i in SETTINGS['colors']}

    random_rules()

    for c in SETTINGS['colors']:
        
        x0 = float(input("(x) From where: "))
        xf = float(input("(x) To where: "))
        y0 = float(input("(y) From where: "))
        yf = float(input("(y) To where: "))
        
        atoms.extend(create(number_of_atoms_per_color, c, x0, xf, y0, yf))

    clusters.clear()



def draw_square(surface, x, y, color, radius):
    pygame.draw.rect(surface, color, (x - radius, y - radius, 2 * radius, 2 * radius))

def draw_circle(surface, x, y, color, radius, fill=True):
    pygame.draw.circle(surface, color, (x, y), radius, 0 if fill else 1)

def draw_line_between_atoms(surface, ax, ay, bx, by, color):
    pygame.draw.line(surface, color, (ax, ay), (bx, by))


atoms = []
clusters = []
total_v = 0

def apply_rules():
    global total_v
    total_v = 0.0
    forces = []
    for a in atoms:
        fx = 0
        fy = 0
        idx = a[4] * SETTINGS['numColors']
        r2 = SETTINGS['radii2Array'][a[4]]
        for b in atoms:
            g = SETTINGS['rulesArray'][idx + b[4]]
            dx = a[0] - b[0]
            dy = a[1] - b[1]
            if dx != 0 or dy != 0:
                d = dx * dx + dy * dy
                if d < r2:
                    F = g / math.sqrt(d)
                    fx += F * dx
                    fy += F * dy
                    if SETTINGS['drawings']['lines']:
                        draw_line_between_atoms(screen, a[0], a[1], b[0], b[1], SETTINGS['color_map'][b[4]])
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
    total_v /= len(atoms)

set_number_of_colors()
random_rules()
place_atoms(SETTINGS['atoms']['count'], True)

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(SETTINGS['drawings']['background_color'])
    apply_rules()

    for a in atoms:
        if SETTINGS['drawings']['circle']:
            draw_circle(screen, a[0], a[1], SETTINGS['color_map'][a[4]], SETTINGS['atoms']['radius'])
        else:
            draw_square(screen, a[0], a[1], SETTINGS['color_map'][a[4]], SETTINGS['atoms']['radius'])

    pygame.display.flip()
    clock.tick(60)

pygame.quit()