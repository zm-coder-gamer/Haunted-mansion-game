import json
import pygame

def load_and_scale_character_images(filename, scaling_factor):
    with open(filename , "r") as file:
        image_data = json.load(file)
    images = {}
    for direction, filenames in image_data.items():
        images[direction] = [pygame.transform.scale(pygame.image.load(f"images/{name}"), (scaling_factor, scaling_factor)) for name in filenames]
    return images