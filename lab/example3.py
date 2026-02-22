from __future__ import annotations

from art import ArtGallery
from designer import Designer

if __name__ == "__main__":
    gallery = ArtGallery(
        {
            "polygon": [
                ["0.0", "0.0"],
                ["12.0", "0.0"],
                ["12.0", "4.0"],
                ["16.0", "4.0"],
                ["16.0", "0.0"],
                ["26.0", "0.0"],
                ["26.0", "14.0"],
                ["20.0", "14.0"],
                ["20.0", "10.0"],
                ["14.0", "10.0"],
                ["14.0", "14.0"],
                ["10.0", "14.0"],
                ["10.0", "20.0"],
                ["14.0", "20.0"],
                ["14.0", "24.0"],
                ["6.0", "24.0"],
                ["6.0", "14.0"],
                ["2.0", "14.0"],
                ["2.0", "8.0"],
                ["0.0", "8.0"],
            ],
            "holes": [
                [
                    ["4.0", "5.0"],
                    ["7.0", "5.0"],
                    ["7.0", "3.0"],
                    ["4.0", "3.0"],
                ],
                [
                    ["19.0", "7.0"],
                    ["23.0", "7.0"],
                    ["23.0", "4.0"],
                    ["19.0", "4.0"],
                ],
            ],
        }
    )
    print(gallery)

    print(f"\nFound {len(gallery.convex_components)} convex components")
    print(f"Found {len(gallery.guards)} potential guard positions")
    Designer(art_gallery=gallery).plot()
