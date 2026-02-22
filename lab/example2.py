from __future__ import annotations

from art import ArtGallery
from designer import Designer

if __name__ == "__main__":
    gallery = ArtGallery(
        {
            "polygon": [
                ["0.0", "0.0"],
                ["10.0", "0.0"],
                ["10.0", "5.0"],
                ["15.0", "5.0"],
                ["15.0", "10.0"],
                ["10.0", "10.0"],
                ["10.0", "15.0"],
                ["5.0", "15.0"],
                ["5.0", "10.0"],
                ["0.0", "10.0"],
            ],
            "holes": [
                [
                    ["2.0", "4.0"],
                    ["4.0", "4.0"],
                    ["4.0", "2.0"],
                    ["2.0", "2.0"],
                ],
                [
                    ["6.0", "14.0"],
                    ["8.0", "14.0"],
                    ["8.0", "12.0"],
                    ["6.0", "12.0"],
                ],
            ],
        }
    )
    print(gallery)

    print(f"\nFound {len(gallery.convex_components)} convex components")
    print(f"Found {len(gallery.guards)} potential guard positions")
    Designer(art_gallery=gallery).plot()
