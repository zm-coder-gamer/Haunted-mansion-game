import pygame

# Doors setup
doors = {}
def create_doors(room_exits):
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
    return doors