import pygame
import random
import math

pygame.init()

W, H = 1000, 500
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

colors = {
    "red": (255, 80, 80),
    "green": (80, 255, 80),
    "blue": (80, 80, 255)
}
PARTICLE_RADIUS = 3

particles = []

class Particle:
    def __init__(self, x, y, color_name):
        self.x = x
        self.y = y
        self.color_name = color_name
        
    def draw(self):
        pygame.draw.circle(screen, colors[self.color_name], (int(self.x), int(self.y)), PARTICLE_RADIUS) # last number is the radius
                          
def add_particles(color_name, count):
    for _ in range(count):
        x = random.uniform(0, W)
        y = random.uniform(0, H)
        particles.append(Particle(x, y, color_name))
        
add_particles("red", 5)
add_particles("blue", 5)
        
running = True
while running:
    screen.fill((0, 0, 0))
    for p in particles:
        p.draw()
    
    pygame.display.flip()
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
pygame.quit()