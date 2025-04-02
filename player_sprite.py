import pygame

# === Player Sprite Wrapper for Fireball Collision ===
class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, rect_ref):
        super().__init__()
        self.rect_ref = rect_ref
        self.image = pygame.Surface((1, 1))  # Invisible
        self.rect = rect_ref  # Uses same reference as main player
    def update(self):
        self.rect = self.rect_ref  # Keep updated to actual player position