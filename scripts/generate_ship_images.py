"""Script para gerar imagens placeholder dos navios"""

import os

import pygame

# Initialize pygame
pygame.init()

# Ship configurations: (name, size, color)
ships_config = [
    ("arcade", 2, (0, 191, 255)),  # Deep Sky Blue
    ("argyles_van", 3, (255, 165, 0)),  # Orange
    ("christmas", 3, (220, 20, 60)),  # Crimson
    ("demogorgon", 5, (75, 0, 130)),  # Indigo
    ("scoops_ahoy", 4, (70, 130, 180)),  # Steel Blue
]

# Image size
CELL_SIZE = 40

# Create assets directory if it doesn't exist
assets_dir = "src/assets/ships"
os.makedirs(assets_dir, exist_ok=True)


def create_ship_segment(color, segment_num, total_segments, is_horizontal=True):
    """Create a single ship segment image"""
    surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

    # Draw base color
    pygame.draw.rect(
        surface, color, (2, 2, CELL_SIZE - 4, CELL_SIZE - 4), border_radius=5
    )

    # Draw darker border
    dark_color = tuple(max(0, c - 50) for c in color)
    pygame.draw.rect(
        surface, dark_color, (2, 2, CELL_SIZE - 4, CELL_SIZE - 4), 2, border_radius=5
    )

    # Draw segment indicator (small circle)
    center_x = CELL_SIZE // 2
    center_y = CELL_SIZE // 2

    # Lighter highlight
    light_color = tuple(min(255, c + 80) for c in color)
    pygame.draw.circle(surface, light_color, (center_x, center_y), 6)

    # Draw segment number
    font = pygame.font.Font(None, 20)
    text = font.render(str(segment_num), True, (255, 255, 255))
    text_rect = text.get_rect(center=(center_x, center_y))
    surface.blit(text, text_rect)

    return surface


def create_ship_images(ship_name, size, color):
    """Create all segment images for a ship"""
    print(f"Creating images for {ship_name} (size: {size})...")

    for i in range(size):
        # Create horizontal segment
        segment = create_ship_segment(color, i + 1, size, is_horizontal=True)

        # Save segment
        filename = f"{assets_dir}/{ship_name}_segment_{i + 1}.png"
        pygame.image.save(segment, filename)
        print(f"  Created {filename}")


# Generate all ship images
print("Generating ship images...")
print("-" * 50)

for ship_name, size, color in ships_config:
    create_ship_images(ship_name, size, color)
    print()

print("-" * 50)
print("All ship images generated successfully!")
print(f"Images saved in: {assets_dir}/")

pygame.quit()
