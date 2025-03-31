import pygame
import json
import time

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Haunted Mansion")

# Load room images
rooms = {
    "Grand Entrance": pygame.transform.scale(pygame.image.load("images/Grand Entrance.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Main Hallway": pygame.transform.scale(pygame.image.load("images/Main Hallway.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Dining Room": pygame.transform.scale(pygame.image.load("images/Dining Room.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Kitchen": pygame.transform.scale(pygame.image.load("images/Kitchen.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Pantry": pygame.transform.scale(pygame.image.load("images/Pantry.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Library": pygame.transform.scale(pygame.image.load("images/Library.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Study": pygame.transform.scale(pygame.image.load("images/Study.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Guest Bedroom": pygame.transform.scale(pygame.image.load("images/Guest Bedroom.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Master Bedroom": pygame.transform.scale(pygame.image.load("images/Master Bedroom.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Bathroom": pygame.transform.scale(pygame.image.load("images/Bathroom.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Ballroom": pygame.transform.scale(pygame.image.load("images/Ballroom.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Gallery": pygame.transform.scale(pygame.image.load("images/Gallery.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Servants Quarters": pygame.transform.scale(pygame.image.load("images/Servants Quarters.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Wine Cellar": pygame.transform.scale(pygame.image.load("images/Wine Cellar.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Basement Storage": pygame.transform.scale(pygame.image.load("images/Basement Storage.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Attic": pygame.transform.scale(pygame.image.load("images/Attic.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Secret Passage": pygame.transform.scale(pygame.image.load("images/Secret Passage.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Torture Chamber": pygame.transform.scale(pygame.image.load("images/Torture Chamber.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Garden Courtyard": pygame.transform.scale(pygame.image.load("images/Garden Courtyard.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Exit Gate": pygame.transform.scale(pygame.image.load("images/Exit Gate.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    "Inventory": pygame.transform.scale(pygame.image.load("images/Inventory.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
}
current_room = "Grand Entrance"
previous_room = None  # Tracks the last room before Inventory
last_inventory_toggle = 0  # Tracks last time inventory was toggled
inventory_cooldown = 300  # milliseconds
# Room dictionaries, values are stored as tuples
room_exits = {
    "Grand Entrance": {"south": "Library", "east": "Main Hallway"},
    "Main Hallway": {"west": "Grand Entrance", "east": "Dining Room", "south": "Study"},
    "Dining Room": {"west": "Main Hallway", "east": "Kitchen", "south": "Guest Bedroom"},
    "Kitchen": {"west": "Dining Room", "east": "Pantry", "south": "Master Bedroom"},
    "Pantry": {"west": "Kitchen", "south": "Bathroom"},
    "Library": {"north": "Grand Entrance", "south": "Ballroom", "east": "Study"},
    "Study": {"north": "Main Hallway", "south": "Gallery", "west": "Library", "east": "Guest Bedroom"},
    "Guest Bedroom": {"north": "Dining Room", "south": "Servants Quarters", "west": "Study", "east": "Master Bedroom"},
    "Master Bedroom": {"north": "Kitchen", "south": "Wine Cellar", "west": "Guest Bedroom", "east": "Bathroom"},
    "Bathroom": {"north": "Pantry", "south": "Basement Storage", "west": "Master Bedroom"},
    "Ballroom": {"north": "Library", "south": "Attic", "east": "Gallery"},
    "Gallery": {"north": "Study", "south": "Secret Passage", "west": "Ballroom", "east": "Servants Quarters"},
    "Servants Quarters": {"north": "Guest Bedroom", "south": "Torture Chamber", "west": "Gallery", "east": "Wine Cellar"},
    "Wine Cellar": {"north": "Master Bedroom", "west": "Servants Quarters", "east": "Basement Storage"},
    "Basement Storage": {"north": "Bathroom", "west": "Wine Cellar"},
    "Attic": {"north": "Ballroom", "east": "Secret Passage"},
    "Secret Passage": {"north": "Gallery", "west": "Attic", "east": "Torture Chamber"},
    "Torture Chamber": {"north": "Servants Quarters", "west": "Secret Passage", "east": "Garden Courtyard"},
    "Garden Courtyard": {"west": "Torture Chamber", "east": "Exit Gate"},
    "Exit Gate": {"west": "Garden Courtyard"},
    "Inventory": {}
}

# Doors setup
doors = {}
def create_doors():
    for room, exits in room_exits.items():
        doors[room] = []
        if "north" in exits:
            doors[room].append(("north", pygame.Rect(370, 30, 60, 20)))
        if "south" in exits:
            doors[room].append(("south", pygame.Rect(370, 550, 60, 20)))
        if "west" in exits:
            doors[room].append(("west", pygame.Rect(30, 270, 20, 60)))
        if "east" in exits:
            doors[room].append(("east", pygame.Rect(750, 270, 20, 60)))
create_doors()

# Room boundaries
wall_thickness = 30
room_bounds = [
    pygame.Rect(0, 0, SCREEN_WIDTH, wall_thickness),
    pygame.Rect(0, SCREEN_HEIGHT - wall_thickness, SCREEN_WIDTH, wall_thickness),
    pygame.Rect(0, 0, wall_thickness, SCREEN_HEIGHT),
    pygame.Rect(SCREEN_WIDTH - wall_thickness, 0, wall_thickness, SCREEN_HEIGHT)
]

# Enemy setup
enemy_rooms = ["Main Hallway", "Ballroom", "Torture Chamber", "Servants Quarters", "Basement Storage", "Kitchen"]
enemies = {}
enemy_speed = 2.9
room_entry_time = None

for room in enemy_rooms:
    enemies[room] = [
        pygame.Rect(420, 290, 30, 30)
    ]

# Load item images
health_potion_img = pygame.image.load("images/health_potion.png")
health_potion_img = pygame.transform.scale(health_potion_img, (40, 40))
key_img = pygame.image.load("images/key.png")
key_img = pygame.transform.scale(key_img, (40, 40))

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
        player_images[direction][i] = pygame.transform.scale(player_images[direction][i], (40, 40))


current_room = "Grand Entrance"
previous_room = None
last_inventory_toggle = 0
inventory_cooldown = 300

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
    "Servants Quarters": [(pygame.Rect(450, 450, 30, 30), "key")]
}


# Load item images
health_potion_img = pygame.image.load("images/health_potion.png")
health_potion_img = pygame.transform.scale(health_potion_img, (40, 40))
key_img = pygame.image.load("images/key.png")
key_img = pygame.transform.scale(key_img, (40, 40))

# Player setup
player = pygame.Rect(100, 300, 40, 40)
player_speed = 5
health = 5

# Animation state
player_facing = "front"
player_frame = 0
player_anim_timer = 0
player_anim_delay = 200  # milliseconds

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

running = True
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

        keys = pygame.key.get_pressed()
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
                        health = min(health + 1, 5)
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

        if current_room in enemy_rooms:
            if room_entry_time and time.time() - room_entry_time >= 0.15:
                for enemy in enemies[current_room]:
                    dx, dy = player.x - enemy.x, player.y - enemy.y
                    dist = max((dx ** 2 + dy ** 2) ** 0.5, 1)
                    enemy.x += enemy_speed * dx / dist
                    enemy.y += enemy_speed * dy / dist

                    if player.colliderect(enemy):
                        health -= 1
                        player.x -= 50
                        player.y -= 50
                        if health <= 0:
                            print("You Died!")
                            running = False

            for enemy in enemies[current_room]:
                pygame.draw.ellipse(screen, (0, 255, 0), enemy)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
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
                    room_entry_time = time.time() if current_room in enemy_rooms else None
                    if direction == "north":
                        player.x, player.y = 400, 500
                    elif direction == "south":
                        player.x, player.y = 400, 100
                    elif direction == "west":
                        player.x, player.y = 700, 300
                    elif direction == "east":
                        player.x, player.y = 100, 300
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
            room_entry_time = time.time() if current_room in enemy_rooms else None

    clock.tick(60)

pygame.quit()
