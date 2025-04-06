import pygame

# === AcidDrop Class ===
# This class defines a green droplet that moves horizontally across the screen
# during the acid rain challenge in the Garden Courtyard.
class AcidDrop(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((0, 255, 0))  # Green acid drop
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.x += self.speed