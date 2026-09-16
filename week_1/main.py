import pygame
import numpy as np
import random

# Configuration

WIDTH = 800
HEIGHT = 800

BOWL_CENTER = np.array([WIDTH / 2, HEIGHT / 2], dtype=float)
BOWL_RADIUS = 300

# Start with 1 ball, then 2. Many at once is the bonus.
NUM_PARTICLES = 1
PARTICLE_RADIUS = 12
PARTICLE_SPEED = 150.0

# Pixels per second squared, not m/s^2. Note that +y points DOWN on screen.
GRAVITY = 900.0

# How much speed survives a bounce. 1.0 loses nothing, below 1.0 is weaker.
WALL_RESTITUTION = 1
RESTITUTION = 1

FPS = 60

positions = []
velocities = []

for i in range(NUM_PARTICLES):

    # A random spot inside the bowl, with the whole ball fitting.
    angle = random.uniform(0, 2 * np.pi)
    distance = random.uniform(0, BOWL_RADIUS - PARTICLE_RADIUS)

    positions.append(BOWL_CENTER + distance * np.array([
        np.cos(angle),
        np.sin(angle)
    ]))

    # A random direction, at roughly PARTICLE_SPEED.
    # Swap for np.array([0.0, 0.0]) to drop the ball from rest.
    angle = random.uniform(0, 2 * np.pi)

    velocities.append(PARTICLE_SPEED * np.array([
        np.cos(angle),
        np.sin(angle)
    ]))

# Pygame setup

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Particle Simulation")

clock = pygame.time.Clock()

running = True

# Main loop

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    # Seconds since the last frame. This is your timestep.
    dt = clock.tick(FPS) / 1000.0

    ###########################################################################
    # TODO: Make every ball fall, and bounce it off the wall of the bowl.     #
    #                                                                         #
    # Two things happen here, in an order that matters.                       #
    #                                                                         #
    # First, it falls. Gravity is an acceleration, so ask yourself what it    #
    # changes directly: the position, or the velocity? And once that has      #
    # changed, what does the ball's new position depend on?                   #
    #                                                                         #
    # Second, it has to stay in the bowl. Work out how you would even         #
    # tell that it has escaped, given that you know where the centre of       #
    # the bowl is, how wide the bowl is, and how wide the ball is.            #
    # Careful: the ball is drawn with a radius of its own, so its edge        #
    # reaches the wall before its centre would.                               #
    #                                                                         #
    # Once you know it has escaped, two things need fixing. Where should      #
    # the ball actually be, and what should its velocity become? For the      #
    # velocity, only the part heading into the wall should change. The        #
    # part sliding along the wall carries on untouched. WALL_RESTITUTION      #
    # decides how much of the incoming speed comes back out.                  #
    ###########################################################################
    
    # CODE STARTS HERE.
    for i in range(NUM_PARTICLES):
        # First update the velocity vectors to account for gravity.
        velocities[i] += np.array([0.0, GRAVITY]) * dt          # Adds 0.0 to the horizontal component and GRAVITY value to vertical component
        
        # Update the position vectors based on the new velocities
        positions[i] += velocities[i] * dt

        # Check if the ball has escaped the wall
        dist_between_centres = positions[i] - BOWL_CENTER
        distance = np.linalg.norm(dist_between_centres)             # np.linalg.norm() basically just finds the magnitude of the vector
        max_allowed_distance = BOWL_RADIUS - PARTICLE_RADIUS

        if distance > max_allowed_distance:
            # Create a unit vector pointing radially outwards from the bowl center
            normal = dist_between_centres / distance
            
            # Put the ball back in the arena
            # NOTE: It was tripping me up that's why I'm writing this:
            # We do not 'move' the ball, instead we teleport it to the max allowed distance, touching the wall of the bowl.
            positions[i] = BOWL_CENTER + normal * max_allowed_distance
            
            # Find the component of the velocity perpendicular to the wall
            v_normal = np.dot(velocities[i], normal)
            
            # Only bounce if the ball is actively moving outward into the wall
            # NOTE: Since this if block is wrapped inside another if block (if distance > max_allowed_distance), the code works
            # If not done this way then the velocity would be changed even if the particle was inside, but not touching the boundary.
            # else the condition would be (if v_normal > 0 and distance > max_allowed_distance)
            if v_normal > 0:
                velocities[i] -= (1.0 + WALL_RESTITUTION) * v_normal * normal

    ###########################################################################
    #                            END OF YOUR CODE                             #
    ###########################################################################

    ###########################################################################
    # TODO: Make the balls bounce off each other.                             #
    #                                                                         #
    # Start with the condition. Given two balls, what has to be true          #
    # about where they are for them to be touching? Every ball has the        #
    # same radius, which makes this simpler than it sounds.                   #
    #                                                                         #
    # Then the response. A collision changes velocities, not positions.       #
    # Which direction does the change act along, and how would you get        #
    # that direction from the two positions you have? Only the motion         #
    # along that direction matters, the rest is unaffected.                   #
    #                                                                         #
    # One trap worth thinking about: two balls that are overlapping but       #
    # already moving apart should be left alone. If you bounce them again     #
    # they will get stuck together. How would you tell "approaching"          #
    # from "separating"?                                                      #
    #                                                                         #
    # Finally, this has to happen for every pair of balls, not just one.      #
    ###########################################################################

    # CODE STARTS HERE.
    for i in range(NUM_PARTICLES):
        for j in range(i + 1, NUM_PARTICLES):
            # Check if the two balls are overlapping
            delta_pos = positions[i] - positions[j]
            distance = np.linalg.norm(delta_pos)
            min_distance = 2 * PARTICLE_RADIUS

            if distance < min_distance:
                # Normal vector pointing from ball i toward ball j
                normal = delta_pos / distance if distance > 0 else np.array([1.0, 0.0])
                
                # Calculate relative velocity between the pair
                rel_velocity = velocities[i] - velocities[j]
                v_rel_normal = np.dot(rel_velocity, normal)
                
                # Only bounce if they are moving TOWARD each other
                if v_rel_normal < 0:
                    impulse = (1.0 + RESTITUTION) * v_rel_normal / 2.0
                    
                    velocities[i] -= impulse * normal
                    velocities[j] += impulse * normal

                    # Push them apart so they stop overlapping
                    overlap = min_distance - distance
                    correction = (overlap / 2.0) * normal
                    positions[i] += correction
                    positions[j] -= correction

    ###########################################################################
    #                            END OF YOUR CODE                             #
    ###########################################################################

    # Render

    screen.fill((20, 20, 25))

    pygame.draw.circle(
        screen,
        (180, 180, 180),
        BOWL_CENTER.astype(int),
        BOWL_RADIUS,
        width=3
    )

    for position in positions:
        pygame.draw.circle(
            screen,
            (220, 220, 220),
            position.astype(int),
            PARTICLE_RADIUS
        )

    pygame.display.flip()

pygame.quit()
