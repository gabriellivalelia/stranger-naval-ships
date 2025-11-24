#!/usr/bin/env python3
"""Generate Laboratory ship segment images"""

import pygame

pygame.init()

# Laboratory ship - 2 segments (gray metallic with green accents)
color = (169, 169, 169)  # Dark Gray
size = 40

for i in range(1, 3):
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))

    # Main rectangle
    pygame.draw.rect(surface, color, (2, 2, size - 4, size - 4), border_radius=4)

    # Accent lines (green experiments)
    accent_color = (100, 200, 100)
    for y in range(10, size - 10, 8):
        pygame.draw.line(surface, accent_color, (8, y), (size - 8, y), 1)

    # Border
    pygame.draw.rect(
        surface, (50, 50, 50), (2, 2, size - 4, size - 4), 2, border_radius=4
    )

    # Segment number
    font = pygame.font.Font(None, 18)
    text = font.render(str(i), True, (255, 255, 255))
    text_rect = text.get_rect(center=(size // 2, size // 2))
    surface.blit(text, text_rect)

    pygame.image.save(surface, f"src/assets/ships/laboratory_segment_{i}.png")
    print(f"✅ Generated: laboratory_segment_{i}.png")

print("\n✅ Laboratory ship images generated successfully!")
pygame.quit()
