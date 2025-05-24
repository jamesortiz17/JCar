import pygame
import math
from time import sleep
from JDist import JDist
import RPi.GPIO as GPIO

# --- SENSOR SETUP ---
center_sensor = JDist(trig=19, echo=26)
left_sensor   = JDist(trig=23, echo=18)
right_sensor  = JDist(trig=25, echo=24)

# --- PYGAME SETUP ---
pygame.init()
WIDTH, HEIGHT = 400, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3-Sensor Radar")
clock = pygame.time.Clock()
CENTER = (WIDTH // 2, HEIGHT // 2)

# Maximum distance you expect (cm) and scale (px/cm)
MAX_DIST = 200
SCALE = (min(WIDTH, HEIGHT) // 2) / MAX_DIST

# Assign each sensor an angle (0° is to the right, 90° is up)
ANGLES = {
    'left':   135,   # upper-left
    'center': 90,    # straight up
    'right':  45     # upper-right
}

# --- INITIAL SENSOR DISTANCES ---
d = {
    'left':   100,
    'center': 100,
    'right':  100
}

running = True
try:
    while running:
        # handle quit
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        # read distances (keep last good if bad reading)
        for name, sensor in [('left', left_sensor), ('center', center_sensor), ('right', right_sensor)]:
            dist = sensor.read_distance()
            if 0 < dist <= MAX_DIST:
                d[name] = dist

        # clear to black
        screen.fill((0, 0, 0))

        # draw concentric range circles
        for r_cm in range(50, MAX_DIST + 1, 50):
            pygame.draw.circle(screen, (50, 50, 50), CENTER, int(r_cm * SCALE), 1)

        # plot each sensor
        for name, dist_cm in d.items():
            θ = math.radians(ANGLES[name])
            px = CENTER[0] + dist_cm * SCALE * math.cos(θ)
            py = CENTER[1] - dist_cm * SCALE * math.sin(θ)
            # dot
            pygame.draw.circle(screen, (0, 255, 0), (int(px), int(py)), 5)
            # beam line
            pygame.draw.line(screen, (0, 255, 0), CENTER, (int(px), int(py)), 1)

        pygame.display.flip()
        clock.tick(10)  # ~10 FPS
        sleep(0.01)

finally:
    print("Cleaning up...")
    GPIO.cleanup()
    pygame.quit()
