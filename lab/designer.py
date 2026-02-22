from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from colorama import Fore

from exceptions import ArtGalleryError, DesignerInvalidDrawableError

if TYPE_CHECKING:
    from convex import ConvexComponent
    from guard import Guard
    from model import ModelMap
    from point import Point, PointSequence
    from polygon import Polygon
    from triangle import Triangle
    from visibility import Visibility


class Drawable(ABC):
    @property
    @abstractmethod
    def points(self) -> PointSequence: ...  # noqa

    @property
    @abstractmethod
    def boundary(self) -> Polygon: ...  # noqa

    @property
    @abstractmethod
    def obstacles(self) -> list[Polygon]: ...  # noqa

    @property
    @abstractmethod
    def ears(self) -> list[Triangle]: ...  # noqa

    @property
    @abstractmethod
    def convex_components(self) -> ModelMap[ConvexComponent]: ...  # noqa

    @property
    @abstractmethod
    def guards(self) -> ModelMap[Guard]: ...  # noqa

    @property
    @abstractmethod
    def visibility(self) -> Visibility[Point]: ...  # noqa


class Designer:
    def __init__(self, *, drawable: Drawable) -> None:
        if not isinstance(drawable, Drawable):
            raise DesignerInvalidDrawableError(
                f"drawable must be a Drawable, got {type(drawable).__name__}"
            )
        self.drawable = drawable

    def plot(self) -> None:
        plt.figure(figsize=(7, 7))
        if len(self.drawable.points) > 0:
            stitched_x = [int(point[0]) for point in self.drawable.points] + [
                int(self.drawable.points[0][0])
            ]
            stitched_y = [int(point[1]) for point in self.drawable.points] + [
                int(self.drawable.points[0][1])
            ]
            plt.plot(
                stitched_x,
                stitched_y,
                "-",
                color="gray",
                linewidth=0.8,
                alpha=0.25,
                zorder=0,
                label="Stitched (bridges)",
            )
        p_x = [int(point[0]) for point in self.drawable.boundary.points] + [
            int(self.drawable.boundary.points[0][0])
        ]
        p_y = [int(point[1]) for point in self.drawable.boundary.points] + [
            int(self.drawable.boundary.points[0][1])
        ]
        plt.plot(p_x, p_y, "k-", linewidth=2, label="Boundary")
        for i, hole in enumerate(self.drawable.obstacles):
            h_x = [int(point[0]) for point in hole.points] + [int(hole.points[0][0])]
            h_y = [int(point[1]) for point in hole.points] + [int(hole.points[0][1])]
            plt.plot(h_x, h_y, "k-", linewidth=2)
            plt.fill(h_x, h_y, "gray", alpha=0.3, label="Hole" if i == 0 else None)
        try:
            for i, ear in enumerate(self.drawable.ears):
                e_x = [int(ear[0][0]), int(ear[1][0]), int(ear[2][0]), int(ear[0][0])]
                e_y = [int(ear[0][1]), int(ear[1][1]), int(ear[2][1]), int(ear[0][1])]
                plt.plot(
                    e_x,
                    e_y,
                    "--",
                    color="lightgray",
                    linewidth=0.8,
                    alpha=0.35,
                    zorder=1,
                    label="Ears" if i == 0 else None,
                )
        except ArtGalleryError as error:
            print(f"{Fore.RED}Ears not shown: {type(error)}: {error}{Fore.RESET}")
        try:
            for i, component in enumerate(self.drawable.convex_components.values()):
                c_x = [int(point[0]) for point in component.polygon.points] + [
                    int(component.polygon.points[0][0])
                ]
                c_y = [int(point[1]) for point in component.polygon.points] + [
                    int(component.polygon.points[0][1])
                ]
                plt.plot(
                    c_x,
                    c_y,
                    "--",
                    color="darkred",
                    linewidth=1.2,
                    alpha=0.7,
                    zorder=2,
                    label="Convex Component" if i == 0 else None,
                )
        except ArtGalleryError as error:
            print(
                f"{Fore.RED}Convex components not shown: {type(error)}: {error}{Fore.RESET}"
            )
        try:
            g_x = [int(guard.position[0]) for guard in self.drawable.guards.values()]
            g_y = [int(guard.position[1]) for guard in self.drawable.guards.values()]
            plt.scatter(
                g_x, g_y, color="red", marker="o", s=100, label="Guards", zorder=5
            )
            v_x: list[float] = []
            v_y: list[float] = []
            for guard in self.drawable.guards.values():
                for point in self.drawable.visibility[guard.id]:
                    v_x.append(int(point[0]))
                    v_y.append(int(point[1]))
            if v_x:
                plt.scatter(
                    v_x,
                    v_y,
                    color="darkred",
                    marker="o",
                    s=20,
                    alpha=0.7,
                    label="Visibility",
                    zorder=4,
                )
        except ArtGalleryError as error:
            print(f"{Fore.RED}Guards not shown: {type(error)}: {error}{Fore.RESET}")
        plt.legend()
        plt.axis("equal")
        plt.title("Art Gallery")
        plt.show()
