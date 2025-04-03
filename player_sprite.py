import pygame

# === Player Sprite Wrapper for Fireball Collision ===
# This is a simple invisible sprite that wraps the main player rect.
# It's used for sprite-based collision checks like with fireballs.
class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, rect_ref):
        super().__init__()
        self.rect_ref = rect_ref  # Store reference to player's rect
        self.image = pygame.Surface((1, 1))  # Tiny invisible surface
        self.rect = rect_ref  # Match player position for collision detection

    def update(self):
        # Keep synced with player's actual rect every frame
        self.rect = self.rect_ref
