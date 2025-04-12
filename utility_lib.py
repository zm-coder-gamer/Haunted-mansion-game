import json
import pygame

def load_and_scale_character_images(filename, scaling_factor):
    with open(filename , "r") as file:
        image_data = json.load(file)
    images = {}
    for direction, filenames in image_data.items():
        images[direction] = [pygame.transform.scale(pygame.image.load(f"images/{name}"), (scaling_factor, scaling_factor)) for name in filenames]
    return images

def load_items_in_rooms(data):
    items_in_rooms={}
    for room, items in data.items():
        items_in_rooms[room] = []
        for item_data in items:
            rect_data = item_data["rect"]
            rect = pygame.Rect(
                rect_data["x"],
                rect_data["y"],
                rect_data["width"],
                rect_data["height"]
            )
            item = item_data["item"]
            items_in_rooms[room].append((rect, item))
    return items_in_rooms