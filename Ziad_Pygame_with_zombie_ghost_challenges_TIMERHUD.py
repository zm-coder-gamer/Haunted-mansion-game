import pygame
import json
import time
import random
from my_lib import create_doors
from player_sprite import PlayerSprite
from fireball import Fireball

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Haunted Mansion")

# === Fireball Challenge Logic ===
def fireball_challenge_logic(current_room, player, fireballs, fireball_timer, dodged_fireballs,
                             dodge_target, dodge_goal_achieved):
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
        if fireball.rect.top > SCREEN_HEIGHT:
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

# Fireball Challenge State
fireballs = pygame.sprite.Group()
fireball_timer = 0
dodged_fireballs = 0
dodge_target = 100
dodge_goal_achieved = False
# Fireball Challenge Tracking for Wine Cellar
wine_cellar_challenge_started = False
wine_cellar_entry_time = None

# === AcidDrop Class ===
class AcidDrop(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((0, 255, 0))  # Green acid drop
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.x += self.speed

# === Acid Rain Challenge State ===
acid_drops = pygame.sprite.Group()
acid_timer = 0
acid_dodged = 0
acid_dodge_target = 200
acid_challenge_started = False
acid_challenge_completed = False
acid_challenge_entry_time = None

current_room = "Grand Entrance" # Player Enters the Mansion
previous_room = None  # Tracks the last room before Inventory
last_inventory_toggle = 0  # Tracks last time inventory was toggled
inventory_cooldown = 300  # milliseconds

# Room dictionaries, values are stored as tuples
# Load JSON data
with open("rooms_data.json", "r") as file:
    room_exits = json.load(file)

# Load room images
all_rooms = room_exits.keys()
rooms = {}
for room in all_rooms:
    rooms[room] = pygame.transform.scale(pygame.image.load("images/"+room+".png"), (SCREEN_WIDTH, SCREEN_HEIGHT))

doors = create_doors(room_exits)

# Room boundaries
wall_thickness = 30
room_bounds = [
    pygame.Rect(0, 0, SCREEN_WIDTH, wall_thickness),
    pygame.Rect(0, SCREEN_HEIGHT - wall_thickness, SCREEN_WIDTH, wall_thickness),
    pygame.Rect(0, 0, wall_thickness, SCREEN_HEIGHT),
    pygame.Rect(SCREEN_WIDTH - wall_thickness, 0, wall_thickness, SCREEN_HEIGHT)
]

# Load item images
health_potion_img = pygame.image.load("images/health_potion.png")
health_potion_img = pygame.transform.scale(health_potion_img, (40, 40))
key_img = pygame.image.load("images/key.png")
key_img = pygame.transform.scale(key_img, (50, 50))

# Load player images
player_images = {
    "front": [
        pygame.image.load("images/player_front.png"),
        pygame.image.load("images/front_walk1.png"),
        pygame.image.load("images/front_walk2.png")
    ],
    "back": [
        pygame.image.load("images/player_back.png"),
        pygame.image.load("images/back_walk1.png"),
        pygame.image.load("images/back_walk2.png")
    ],
    "left": [
        pygame.image.load("images/player_left.png"),
        pygame.image.load("images/left_walk1.png"),
        pygame.image.load("images/left_walk2.png")
    ],
    "right": [
        pygame.image.load("images/player_right.png"),
        pygame.image.load("images/right_walk1.png"),
        pygame.image.load("images/right_walk2.png")
    ]
}

# Scale all player images
for direction in player_images:
    for i in range(len(player_images[direction])):
        player_images[direction][i] = pygame.transform.scale(player_images[direction][i], (70, 70))

# Animation state
player_facing = "front"
player_frame = 0
player_anim_timer = 0
player_anim_delay = 200  # milliseconds

# Player setup
player = pygame.Rect(80, 275, 70, 70)
player_sprite = PlayerSprite(player)
player_speed = 4
health = 1000

# Helper to get adjusted speed per room
def get_enemy_speed(entity_type, room):
    if entity_type == "zombie":
        return 2.01 if room == "Servants Quarters" else 3.2
    elif entity_type == "ghost":
        return 2.02 if room == "Basement Storage" else 3.3
    return 3


# Load zombie images
zombie_images = {
    "left": [
        pygame.image.load("images/zombie_left.png"),
        pygame.image.load("images/zleft_run1.png"),
        pygame.image.load("images/zleft_run2.png")
    ],
    "right": [
        pygame.image.load("images/zombie_right.png"),
        pygame.image.load("images/zright_run1.png"),
        pygame.image.load("images/zright_run2.png")
    ]
}

# Scale all zombie images
for direction in zombie_images:
    for i in range(len(zombie_images[direction])):
        zombie_images[direction][i] = pygame.transform.scale(zombie_images[direction][i], (100, 100))

# zombie setup
zombie_rooms = ["Main Hallway", "Torture Chamber", "Servants Quarters", "Wine Cellar", "Gallery"]
zombies = {}

for room in zombie_rooms:
    zombies[room] = [
        pygame.Rect(420, 290, 85, 85)
    ]

# Zombie animation state
zombie_frame = 0
zombie_anim_timer = 0
zombie_anim_delay = 300
zombie_facing = {}  # tracks zombie facing per room
room_entry_time = time.time()
knockback_force = 50

# Load ghost images (hovering cycle)
ghost_images = {
    "left": [
        pygame.image.load("images/ghost1_left.png"),
        pygame.image.load("images/ghost2_left.png"),
        pygame.image.load("images/ghost3_left.png")
    ],
    "right": [
        pygame.image.load("images/ghost1_right.png"),
        pygame.image.load("images/ghost2_right.png"),
        pygame.image.load("images/ghost3_right.png")
    ]
}

# Scale all ghost images
for direction in ghost_images:
    for i in range(len(ghost_images[direction])):
        ghost_images[direction][i] = pygame.transform.scale(ghost_images[direction][i], (100, 100))

ghost_frame = 0
ghost_anim_timer = 0
ghost_anim_delay = 200

ghosts = {
    "Ballroom": [pygame.Rect(300, 300, 80, 80)]
}

# Inventory setup
inventory = []
max_inventory_slots = 20
inventory_cursor = pygame.Rect(10, 10, 40, 40)
cursor_speed = 5

# Load item images
health_potion_img = pygame.image.load("images/health_potion.png")
health_potion_img = pygame.transform.scale(health_potion_img, (40, 40))
key_img = pygame.image.load("images/key.png")
key_img = pygame.transform.scale(key_img, (40, 40))

# Inventory setup
inventory = []
max_inventory_slots = 20
inventory_cursor = pygame.Rect(10, 10, 40, 40)
cursor_speed = 5

# Items in rooms
items_in_rooms = {
    "Grand Entrance": [(pygame.Rect(100, 100, 30, 30), "health_potion")],
    "Master Bedroom": [(pygame.Rect(500, 400, 30, 30), "health_potion")],
    "Guest Bedroom": [(pygame.Rect(120, 120, 30, 30), "key")],
    "Torture Chamber": [(pygame.Rect(450, 450, 30, 30), "key")]
}

# Locked doors setup
locked_doors = {
    ("Ballroom", "south"): True,  # The south door in Ballroom is locked
    ("Gallery", "south"): True    # Locked from outside until accessed from Secret Passage
}

# Doors setup with lock state
for room, door_list in doors.items():
    for i, (direction, rect) in enumerate(door_list):
        if (room, direction) in locked_doors and locked_doors[(room, direction)]:
            door_list[i] = (direction, rect, True)  # locked
        else:
            door_list[i] = (direction, rect, False)  # unlocked


# === Challenge Room Survival Timers ===
zombie_challenge_started = False
zombie_challenge_completed = False
zombie_challenge_start_time = None
zombie_challenge_duration = 20  # seconds

ghost_challenge_started = False
ghost_challenge_completed = False
ghost_challenge_start_time = None
ghost_challenge_duration = 20  # seconds

running = True

# Intro prompt state
I_tracker = 0
def pressed_I(keys):
    global I_tracker
    if keys[pygame.K_i]:
        I_tracker += 1

inventory_key_pressed = False
show_inventory_hint = True
game_start_time = time.time()

clock = pygame.time.Clock()

# Main game loop
while running:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(rooms[current_room], (0, 0))

    if current_room == "Inventory":
        slot_size = 60
        padding = 10
        columns = SCREEN_WIDTH // (slot_size + padding)
        slot_rects = []

        for i in range(max_inventory_slots):
            row = i // columns
            col = i % columns
            slot_rect = pygame.Rect(col * (slot_size + padding) + padding, row * (slot_size + padding) + padding, slot_size, slot_size)
            slot_rects.append(slot_rect)
            pygame.draw.rect(screen, (100, 100, 100), slot_rect)
            if i < len(inventory):
                if inventory[i] == "health_potion":
                    screen.blit(health_potion_img, slot_rect.topleft)
                elif inventory[i] == "key":
                    screen.blit(key_img, slot_rect.topleft)

        pygame.draw.ellipse(screen, (255, 0, 0), inventory_cursor)
        # === Display Instructions ===
        instruction_font = pygame.font.SysFont(None, 24)

        instructions = [
            "Controls:",
            "- Move: W A S D",
            "- Open Doors: Press O while touching a door",
            "- Inventory: Press I to open/close inventory",
            "- Interact with items: Move red cursor with WASD, press E to use item",
            "",
            "Doors:",
            "- Green = unlocked",
            "- Purple = locked (needs a key)                                                    Goal: Escape the Haunted Mansion",
            "- Some doors can only be unlocked from the other side      Hint: You start in the top left of the map,",
            "- Wine Cellar doors lock during the fireball challenge         The exit is at the Bottom right of the map.",
            "",
            "Gameplay Tips:",
            "- Touch potions or keys to collect them",
            "- Health potions restore 2 health when used",
            "- Use keys on locked doors by pressing O",
            "- Avoid zombies and ghosts — they hurt!"
        ]

        text_y = 150
        for line in instructions:
            text_surface = instruction_font.render(line, True, (0, 0, 0))
            screen.blit(text_surface, (30, text_y))
            text_y += 25  # Line spacing


        keys = pygame.key.get_pressed()
        pressed_I(keys)
        if keys[pygame.K_a]:
            inventory_cursor.x -= cursor_speed
        if keys[pygame.K_d]:
            inventory_cursor.x += cursor_speed
        if keys[pygame.K_w]:
            inventory_cursor.y -= cursor_speed
        if keys[pygame.K_s]:
            inventory_cursor.y += cursor_speed

        if keys[pygame.K_e]:
            for i, rect in enumerate(slot_rects[:len(inventory)]):
                if inventory_cursor.colliderect(rect):
                    if inventory[i] == "health_potion":
                        health = min(health + 2, 10)
                        print("Used health potion")
                        inventory.pop(i)
                        break

    else:
        # Draw player image based on direction and animation
        frame_list = player_images[player_facing]
        frame = frame_list[0] if player_anim_timer == 0 else frame_list[(player_frame % 2) + 1]
        screen.blit(frame, (player.x, player.y))

        # Draw doors with locked color
        for direction, door_rect, is_locked in doors[current_room]:
            color = (128, 0, 128) if is_locked else (0, 255, 0)
            pygame.draw.rect(screen, color, door_rect)

        for wall in room_bounds:
            pygame.draw.rect(screen, (0, 0, 255), wall, 2)

        for wall in room_bounds:
            pygame.draw.rect(screen, (0, 0, 255), wall, 2)

        font = pygame.font.SysFont(None, 36)
        health_text = font.render(f"Health: {health}", True, (255, 0, 0))
        screen.blit(health_text, (10, 10))

        # item pickup system to handle multiple types
        if current_room in items_in_rooms:
            for item_rect, item_type in items_in_rooms[current_room][:]:
                if item_type == "health_potion":
                    screen.blit(health_potion_img, item_rect.topleft)
                elif item_type == "key":
                    screen.blit(key_img, item_rect.topleft)

                if player.colliderect(item_rect) and len(inventory) < max_inventory_slots:
                    inventory.append(item_type)
                    items_in_rooms[current_room].remove((item_rect, item_type))

        if current_room in zombies:
            for index, zombie in enumerate(zombies[current_room]):
                # Determine facing direction
                if player.x > zombie.x:
                    face_dir = "right"
                else:
                    face_dir = "left"
                zombie_facing[index] = face_dir
                # Animate zombie walk
                if current_time - zombie_anim_timer > zombie_anim_delay:
                    zombie_frame = (zombie_frame + 1) % 2
                    zombie_anim_timer = current_time

                # Display idle or walking frame based on room_entry_time
                time_since_entry = time.time() - room_entry_time
                if time_since_entry < 0.35:
                    img = zombie_images[face_dir][0]  # idle
                else:
                    # Chase logic
                    dx, dy = player.x - zombie.x, player.y - zombie.y
                    distance = max((dx ** 2 + dy ** 2) ** 0.5, 1)
                    zombie_speed = get_enemy_speed("zombie", current_room)
                    zombie.x += int(zombie_speed * dx / distance)
                    zombie.y += int(zombie_speed * dy / distance)
                    img = zombie_images[face_dir][zombie_frame + 1]  # walk animation

                    # Collision and knockback
                    if player.colliderect(zombie):
                        health -= 1
                        knock_dx = int(knockback_force * dx / distance)
                        knock_dy = int(knockback_force * dy / distance)
                        player.x += knock_dx
                        player.y += knock_dy
                        # Prevent player from being knocked outside bounds
                        if player.left < 30: player.left = 31
                        if player.right > SCREEN_WIDTH - 30: player.right = SCREEN_WIDTH - 31
                        if player.top < 30: player.top = 30
                        if player.bottom > SCREEN_HEIGHT - 30: player.bottom = SCREEN_HEIGHT - 31
                screen.blit(img, zombie)
        
        # Ghost Code
        if current_room in ghosts:
            if current_time - ghost_anim_timer > ghost_anim_delay:
                ghost_frame = (ghost_frame + 1) % 3
                ghost_anim_timer = current_time

            for ghost in ghosts[current_room]:
                dx, dy = player.x - ghost.x, player.y - ghost.y
                dist = max((dx ** 2 + dy ** 2) ** 0.5, 1)
                ghost_speed = get_enemy_speed("ghost", current_room)
                ghost.x += int(ghost_speed * dx / dist)
                ghost.y += int(ghost_speed * dy / dist)

                # Determine facing direction
                face = "right" if player.x > ghost.x else "left"

                # Draw ghost
                ghost_img = ghost_images[face][ghost_frame]
                screen.blit(ghost_img, ghost)

                if player.colliderect(ghost):
                    health -= 1
                    ghost.x = player.x + int(180 * dx / dist)
                    ghost.y = player.y + int(180 * dy / dist)

        if health <= 0:
            print("You Died!")
            running = False
    
        # === Zombie Dodge Challenge: Servants Quarters === #
        if current_room == "Servants Quarters":
            if not zombie_challenge_started:
                zombie_challenge_started = True
                zombie_challenge_start_time = time.time()

            if zombie_challenge_started and not zombie_challenge_completed:
                if time.time() - zombie_challenge_start_time > zombie_challenge_duration:
                    zombie_challenge_completed = True
                    zombies["Servants Quarters"] = []  # clear all zombies
                    for i, (direction, rect, locked) in enumerate(doors["Servants Quarters"]):
                        doors["Servants Quarters"][i] = (direction, rect, False)
                        locked_doors[("Servants Quarters", direction)] = False
                    # Spawn reward health potion in center
                    items_in_rooms.setdefault("Servants Quarters", []).append(
                        (pygame.Rect(380, 280, 30, 30), "health_potion")
)


            if not hasattr(pygame, "_zombie_challenge_initialized"):
                pygame._zombie_challenge_initialized = True
                # Lock all doors
                for i, (direction, rect, locked) in enumerate(doors["Servants Quarters"]):
                    doors["Servants Quarters"][i] = (direction, rect, True)
                    locked_doors[("Servants Quarters", direction)] = True
                # Spawn more zombies
                zombies["Servants Quarters"] = [
                    pygame.Rect(300, 300, 85, 85),
                    pygame.Rect(400, 300, 85, 85),
                    pygame.Rect(600, 300, 85, 85),
                ]

            if current_room in zombies:
                # Add knockback between zombies
                for i, zombie in enumerate(zombies[current_room]):
                    dx, dy = player.x - zombie.x, player.y - zombie.y
                    dist = max((dx ** 2 + dy ** 2) ** 0.5, 1)
                    speed = get_enemy_speed("zombie", current_room)
                    move_x = int(speed * dx / dist)
                    move_y = int(speed * dy / dist)

                    # Move zombie
                    zombie.x += move_x
                    zombie.y += move_y

                    # Check and apply knockback from other zombies
                    for j, other in enumerate(zombies[current_room]):
                        if i != j and zombie.colliderect(other):
                            repel_dx = zombie.x - other.x
                            repel_dy = zombie.y - other.y
                            repel_dist = max((repel_dx ** 2 + repel_dy ** 2) ** 0.5, 1)
                            knockback_strength = 4
                            zombie.x += int(knockback_strength * repel_dx / repel_dist)
                            zombie.y += int(knockback_strength * repel_dy / repel_dist)

        # === Ghost Dodge Challenge: Basement Storage ===
        if current_room == "Basement Storage":
            if not ghost_challenge_started:
                ghost_challenge_started = True
                ghost_challenge_start_time = time.time()

            if ghost_challenge_started and not ghost_challenge_completed:
                if time.time() - ghost_challenge_start_time > ghost_challenge_duration:
                    ghost_challenge_completed = True
                    ghosts["Basement Storage"] = []  # clear all ghosts
                    for i, (direction, rect, locked) in enumerate(doors["Basement Storage"]):
                        doors["Basement Storage"][i] = (direction, rect, False)
                        locked_doors[("Basement Storage", direction)] = False
                    # Spawn reward health potion in center
                    items_in_rooms.setdefault("Basement Storage", []).append((pygame.Rect(380, 280, 30, 30), "health_potion"))
                        
            if not hasattr(pygame, "_ghost_challenge_initialized"):
                pygame._ghost_challenge_initialized = True
                for i, (direction, rect, locked) in enumerate(doors["Basement Storage"]):
                    doors["Basement Storage"][i] = (direction, rect, True)
                    locked_doors[("Basement Storage", direction)] = True
                ghosts["Basement Storage"] = [
                    pygame.Rect(450, 300, 80, 80),
                    pygame.Rect(600, 300, 80, 80)]

            if current_room in ghosts:
                # Ghost movement and knockback
                for i, ghost in enumerate(ghosts[current_room]):
                    dx, dy = player.x - ghost.x, player.y - ghost.y
                    dist = max((dx ** 2 + dy ** 2) ** 0.5, 1)
                    speed = get_enemy_speed("ghost", current_room)
                    ghost.x += int(speed * dx / dist)
                    ghost.y += int(speed * dy / dist)

                    # Repel from other ghosts
                    for j, other in enumerate(ghosts[current_room]):
                        if i != j and ghost.colliderect(other):
                            repel_dx = ghost.x - other.x
                            repel_dy = ghost.y - other.y
                            repel_dist = max((repel_dx ** 2 + repel_dy ** 2) ** 0.5, 1)
                            knockback_strength = 2
                            ghost.x += int(knockback_strength * repel_dx / repel_dist)
                            ghost.y += int(knockback_strength * repel_dy / repel_dist)

    # Fireball Challenge: Wine Cellar
    if current_room == "Kitchen":
        if wine_cellar_entry_time is None:
            wine_cellar_entry_time = time.time()

        # Start challenge if player enters center zone or 5s passes
        if not wine_cellar_challenge_started:
            if 250 < player.x < 500 or (time.time() - wine_cellar_entry_time) > 5:
                wine_cellar_challenge_started = True
                # Lock both doors for duration of challenge
                for i, (direction, rect, locked) in enumerate(doors["Kitchen"]):
                    if direction in ["west", "east", "south"]:
                        doors["Kitchen"][i] = (direction, rect, True)
                        locked_doors[("Kitchen", direction)] = True

        if wine_cellar_challenge_started:
            fireball_timer, dodged_fireballs, dodge_goal_achieved, player_dead = fireball_challenge_logic(
                current_room, player, fireballs, fireball_timer, dodged_fireballs, dodge_target, dodge_goal_achieved)
            fireballs.draw(screen)

            if player_dead:
                running = False

            font = pygame.font.SysFont(None, 36)
            target_text = font.render("Target: Dodge 100 fireballs", True, (0, 0, 0))
            dodged_text = font.render("Dodged: " + str(min(dodged_fireballs, dodge_target)), True, (0, 128, 0))
            screen.blit(target_text, (10, 40))
            screen.blit(dodged_text, (10, 70))

            # Unlock doors after challenge completion
            if dodge_goal_achieved:
                for i, (direction, rect, locked) in enumerate(doors["Kitchen"]):
                    if direction in ["west", "east", "south"]:
                        doors["Kitchen"][i] = (direction, rect, False)
                        locked_doors[("Kitchen", direction)] = False
    
    # Acid Rain Challenge: Garden Courtyard
    if current_room == "Garden Courtyard":
        if acid_challenge_entry_time is None:
            acid_challenge_entry_time = time.time()

        if not acid_challenge_started:
            if 250 < player.x < 500 or (time.time() - acid_challenge_entry_time) > 5:
                acid_challenge_started = True
                # Lock west and east doors
                for i, (direction, rect, locked) in enumerate(doors["Garden Courtyard"]):
                    if direction in ["west", "east"]:
                        doors["Garden Courtyard"][i] = (direction, rect, True)
                        locked_doors[("Garden Courtyard", direction)] = True

        if acid_challenge_started and not acid_challenge_completed:
            acid_timer += 1
            if acid_timer > 18:
                y = random.randint(50, 550)
                speed = random.choice([-10, -8, -7, -6, 6, 7, 8, 10])
                x = 0 if speed > 0 else 800
                acid_drops.add(AcidDrop(x, y, speed))
                acid_timer = 0

            acid_drops.update()
            acid_drops.draw(screen)

            for drop in acid_drops:
                if drop.rect.right < 0 or drop.rect.left > 800:
                    acid_dodged += 1
                    drop.kill()

            hits = pygame.sprite.spritecollide(player_sprite, acid_drops, True)
            if hits:
                health -= 1
                if health <= 0:
                    running = False

            font = pygame.font.SysFont(None, 28)
            label = font.render(f"Acid Dodged: {acid_dodged}/{acid_dodge_target}", True, (0, 128, 0))
            screen.blit(label, (10, 100))

            if acid_dodged >= acid_dodge_target:
                acid_challenge_completed = True
                for i, (direction, rect, locked) in enumerate(doors["Garden Courtyard"]):
                    if direction in ["west", "east"]:
                        doors["Garden Courtyard"][i] = (direction, rect, False)
                        locked_doors[("Garden Courtyard", direction)] = False
                acid_drops.empty()
    
    # Show instruction to press I in Grand Entrance
    if current_room == "Grand Entrance":
        hint_font = pygame.font.SysFont(None, 28)
        if time.time() - game_start_time > 0.75:
            if I_tracker == 0:
                hint_text = hint_font.render("Press 'I' to open your inventory and view instructions", True, (0, 0, 0))
            else:
                hint_text = hint_font.render(" ", True, (0, 0, 0))
            screen.blit(hint_text, (200, 290))
    
    # === Survival HUDs ===
    if current_room == "Servants Quarters" and zombie_challenge_started and not zombie_challenge_completed:
        font = pygame.font.SysFont(None, 32)
        time_elapsed = int(time.time() - zombie_challenge_start_time)
        label = font.render(f"Survive: {time_elapsed}/{zombie_challenge_duration} seconds", True, (0, 0, 0))
        screen.blit(label, (10, 70))

    if current_room == "Basement Storage" and ghost_challenge_started and not ghost_challenge_completed:
        font = pygame.font.SysFont(None, 32)
        time_elapsed = int(time.time() - ghost_challenge_start_time)
        label = font.render(f"Survive: {time_elapsed}/{ghost_challenge_duration} seconds", True, (0, 0, 0))
        screen.blit(label, (10, 70))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    pressed_I(keys)
    new_x, new_y = player.x, player.y
    moved = False

    if current_room != "Inventory":
        if keys[pygame.K_a]:
            new_x -= player_speed
            player_facing = "left"
            moved = True
        if keys[pygame.K_d]:
            new_x += player_speed
            player_facing = "right"
            moved = True
        if keys[pygame.K_w]:
            new_y -= player_speed
            player_facing = "back"
            moved = True
        if keys[pygame.K_s]:
            new_y += player_speed
            player_facing = "front"
            moved = True

        temp_rect = pygame.Rect(new_x, new_y, player.width, player.height)
        for wall in room_bounds:
            if temp_rect.colliderect(wall): break
        else:
            player.x, player.y = new_x, new_y

        if moved:
            if current_time - player_anim_timer > player_anim_delay:
                player_frame += 1
                player_anim_timer = current_time
        else:
            player_frame = 0  # reset to standing still

        temp_rect = pygame.Rect(new_x, new_y, player.width, player.height)
        for wall in room_bounds:
            if temp_rect.colliderect(wall): break
        else:
            player.x, player.y = new_x, new_y

        for i, (direction, door_rect, is_locked) in enumerate(doors[current_room]):
            if player.colliderect(door_rect) and keys[pygame.K_o]:
                if is_locked:
                    if (current_room, direction) == ("Gallery", "south"):
                        print("This door is locked from the other side.")
                        break
                    # Prevent Kitchen doors from being opened during challenge
                    if (current_room == "Kitchen" and direction in ["west", "east", "south"] and not dodge_goal_achieved):
                        print("This door is locked during the fireball challenge.")
                        break
                    # Prevent Garden Courtyard door opening during acid rain challenge
                    if (current_room == "Garden Courtyard" and direction in ["west", "east"] and not acid_challenge_completed):
                        print("This door is locked during the acid rain challenge.")
                        break
                    # Prevent Servants Quarters door opening during zombie challenge
                    if (current_room == "Servants Quarters" and direction in ["north", "south", "east", "west"] and not zombie_challenge_completed):
                        print("This door is locked during the zombie challenge.")
                        break
                    # Prevent Basement Storage door opening during ghost challenge
                    if (current_room == "Basement Storage" and direction in ["north", "south", "east", "west"] and not ghost_challenge_completed):
                        print("This door is locked during the ghost challenge.")
                        break

                    elif "key" in inventory:
                        inventory.remove("key")
                        doors[current_room][i] = (direction, door_rect, False)
                        locked_doors[(current_room, direction)] = False
                        print("Unlocked door with key")
                    else:
                        print("This door is locked. You need a key.")
                    break
                else:
                    next_room = room_exits[current_room][direction]
                    # Special unlock: if entering Secret Passage from the north, unlock Gallery's south door
                    if current_room == "Secret Passage" and direction == "north":
                        if ("Gallery", "south") in locked_doors:
                            locked_doors[("Gallery", "south")] = False
                            for j, (d, r, locked) in enumerate(doors["Gallery"]):
                                if d == "south":
                                    doors["Gallery"][j] = (d, r, False)
                            print("Unlocked Gallery's south door from inside")

                    current_room = next_room
                    room_entry_time = time.time() if current_room in zombie_rooms else None
                    if direction == "north":
                        player.x, player.y = 375, 475
                    elif direction == "south":
                        player.x, player.y = 375, 70
                    elif direction == "west":
                        player.x, player.y = 675, 275
                    elif direction == "east":
                        player.x, player.y = 75, 275
                    break

    if keys[pygame.K_i] and current_time - last_inventory_toggle > inventory_cooldown:
        last_inventory_toggle = current_time
        if current_room != "Inventory":
            previous_room = current_room
            current_room = "Inventory"
            inventory_cursor.topleft = (375, 300)
            print("Opened Inventory")
        elif current_room == "Inventory" and previous_room:
            current_room = previous_room
            print(f"Returned to {current_room}")
            previous_room = None
            room_entry_time = time.time() if current_room in zombie_rooms else None

    clock.tick(60)
pygame.quit()