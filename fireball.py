import pygame

# === Fireball Class ===
class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, speed):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 165, 0))  # Orange fireball
        self.rect = self.image.get_rect(center=(x, 50))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed