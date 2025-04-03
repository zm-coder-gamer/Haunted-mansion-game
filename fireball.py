import pygame

# === Fireball Class ===
# This class defines a fireball object used in the fireball dodge challenge.
# It inherits from pygame.sprite.Sprite so we can use it in sprite groups.
class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, speed):
        super().__init__()
        # Create a surface for the fireball
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 165, 0))  # Orange color for fireball
        # Create a rectangular area for collision detection
        self.rect = self.image.get_rect(center=(x, 50))
        self.speed = speed

    def update(self):
        # Moves the fireball downward on the screen
        self.rect.y += self.speed
