from __future__ import annotations

from art import ArtGallery

if __name__ == "__main__":
    gallery = ArtGallery(
        {
            "polygon": [
                ["0.0", "0.0"],
                ["1.0", "10.0"],
                ["2.0", "2.0"],
                ["3.0", "2.0"],
                ["4.0", "10.0"],
                ["5.0", "2.0"],
                ["6.0", "2.0"],
                ["7.0", "10.0"],
                ["8.0", "2.0"],
                ["9.0", "2.0"],
                ["10.0", "10.0"],
                ["11.0", "0.0"],
            ],
        }
    )
    print(gallery)
    gallery.plot()
