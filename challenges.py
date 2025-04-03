import pygame
import random
from fireball import Fireball
from player_sprite import PlayerSprite  # Only needed for type hints if desired
# SCREEN_HEIGHT
# fireball_challenge_logic

def fireball_challenge_logic(current_room, player, fireballs, fireball_timer, dodged_fireballs,
                             dodge_target, dodge_goal_achieved, player_sprite, screen_height):
    if current_room != "Kitchen":
        return fireball_timer, dodged_fireballs, dodge_goal_achieved, False

    fireball_timer += 1
    if not dodge_goal_achieved and fireball_timer > 10:
        x = random.randint(70, 740)
        speed = random.choice([6, 7, 8, 10])
        fireball = Fireball(x, speed)
        fireballs.add(fireball)
        fireball_timer = 0

    for fireball in fireballs.sprites():
        if not dodge_goal_achieved:
            fireball.update()
        if fireball.rect.top > screen_height:
            fireball.kill()
            if not dodge_goal_achieved:
                dodged_fireballs += 1
                if dodged_fireballs >= dodge_target:
                    dodge_goal_achieved = True
                    fireballs.empty()

    if not dodge_goal_achieved:
        hits = pygame.sprite.spritecollide(player_sprite, fireballs, True)
        if hits:
            global health
            health -= 1
            if health <= 0:
                print("You Died!")
                fireballs.empty()
                return fireball_timer, dodged_fireballs, dodge_goal_achieved, True

    return fireball_timer, dodged_fireballs, dodge_goal_achieved, False
