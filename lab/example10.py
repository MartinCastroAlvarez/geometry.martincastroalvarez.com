from __future__ import annotations

from art import ArtGallery

if __name__ == "__main__":

    polygon: list[list[str]] = []

    polygon.append(["0.0", "0.0"])
    polygon.append(["1.0", "10.0"])
    polygon.append(["2.0", "2.0"])

    for i in range(10):
        polygon.append([str(3 + 3 * i + 0), "2.0"])
        polygon.append([str(3 + 3 * i + 1), "10.0"])
        polygon.append([str(3 + 3 * i + 2), "2.0"])

    polygon.append([str(3 + 3 * i + 3), "2.0"])
    polygon.append([str(3 + 3 * i + 4), "10.0"])
    polygon.append([str(3 + 3 * i + 5), "0.0"])

    gallery = ArtGallery(
        {
            "polygon": polygon,
        }
    )
    print(gallery)
    gallery.plot()
