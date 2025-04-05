import random
import pygame
from fireball import Fireball
from player_sprite import PlayerSprite

# === Fireball Challenge Logic ===
# This function handles the falling fireball challenge.
# The player must dodge fireballs in the Kitchen for a set amount of time.
def fireball_challenge_logic(current_room, player, fireballs, fireball_timer, dodged_fireballs,
                             dodge_target, dodge_goal_achieved, player_sprite, screen_height, health):
    if current_room != "Kitchen":
        return fireball_timer, dodged_fireballs, dodge_goal_achieved, health, False

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
            health -= 1
            if health <= 0:
                print("You Died!")
                fireballs.empty()
                return fireball_timer, dodged_fireballs, dodge_goal_achieved, health, True
                
    return fireball_timer, dodged_fireballs, dodge_goal_achieved, health, False