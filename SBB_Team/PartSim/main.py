import pygame
import random




pygame.init()
W, H = 1000, 500
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Particle Display")  
clock = pygame.time.Clock()



PARTICLE_COUNT = 200
PREDEFINED_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)] 
PARTICLE_RADIUS = 3


particles = []
for _ in range(PARTICLE_COUNT):
    x = random.randint(PARTICLE_RADIUS, W - PARTICLE_RADIUS) 
    y = random.randint(PARTICLE_RADIUS, H - PARTICLE_RADIUS)
    color = random.choice(PREDEFINED_COLORS)
    particles.append([x, y, color])



running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill((0, 0, 0))
    
    
    for x, y, color in particles:
        pygame.draw.circle(screen, color, (x, y), PARTICLE_RADIUS)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()