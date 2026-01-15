"""Cellular automata cave generation helpers."""

from __future__ import annotations

import random


class tool:

    # TODO verify indentation correction is accurate
    @staticmethod
    def line(x: int, y: int, x2: int, y2: int) -> list[tuple[int, int]]:
        """
        Compute a Bresenham line between two points.

        Args:
            x: Starting x coordinate.
            y: Starting y coordinate.
            x2: Ending x coordinate.
            y2: Ending y coordinate.

        Returns:
            A list of (x, y) coordinates along the line.
        """
        steep = False
        coords: list[tuple[int, int]] = []

        dx = abs(x2 - x)
        dy = abs(y2 - y)
        sx = 1 if (x2 - x) > 0 else -1
        sy = 1 if (y2 - y) > 0 else -1

        if dy > dx:
            steep = True
            x, y = y, x
            dx, dy = dy, dx
            sx, sy = sy, sx

        d = (2 * dy) - dx

        for _ in range(dx):
            coords.append((y, x) if steep else (x, y))
            if d >= 0:
                y += sy
                d -= 2 * dx
            x += sx
            d += 2 * dy

        coords.append((x2, y2))

        return coords


class cave_gen:

    def __init__(self, WIDTH: int, HEIGHT: int, count: int = 0) -> None:
        """
        Initialize cave generator grid.

        Args:
            WIDTH: Grid width.
            HEIGHT: Grid height.
            count: Number of cellular automata iterations to apply initially.
        """
        self.width = WIDTH
        self.height = HEIGHT

        A = []
        for i in range(self.height):
            A.append([0] * self.width)

        for y in range(self.height):
            for x in range(self.width):
                if random.randrange(100) <= 45:
                    tile = 1
                else:
                    tile = 0

                A[y][x] = tile
        self.A = A

        if count > 1:
            self.apply_cell(count)

    def polycut(self) -> None:
        """Carve a random quadrilateral hole in the grid."""
        x1 = random.randrange(0, self.width // 4)
        y1 = random.randrange(0, self.height // 4)

        x2 = random.randrange(self.width - self.width // 4, self.width)
        y2 = random.randrange(0, self.height // 4)

        x3 = random.randrange(0, self.width // 4)
        y3 = random.randrange(self.height - self.height // 4, self.height)

        x4 = random.randrange(self.width - self.width // 4, self.width)
        y4 = random.randrange(self.height - self.height // 4, self.height)

        lines = []
        lines.append(tool.line(x1, y1, x2, y2))
        lines.append(tool.line(x2, y2, x3, y3))
        lines.append(tool.line(x3, y3, x4, y4))
        lines.append(tool.line(x4, y4, x1, y1))

        for line in lines:
            for point in line:
                x, y = point
                self.A[y][x] = 0

    def apply_cell(self, count: int) -> None:
        """Apply cellular automata rules for ``count`` iterations."""
        for _ in range(count):

            # A = self.A
            B = []
            for i in range(self.height):
                B.append([0] * self.width)

            for y in range(self.height):
                for x in range(self.width):
                    if self.checkn(y, x, 4) or self.checkopen(y, x):
                        B[y][x] = 1
            self.A = B

    def checkopen(self, y: int, x: int) -> int:
        """Return 1 if the neighborhood is empty, else 0."""
        A = self.A
        wn = 0
        for r_x in (-2, -1, 0, 1, 2):
            for r_y in (-2, -1, 0, 1, 2):
                b_x = x + r_x
                b_y = y + r_y
                try:
                    if A[b_y][b_x]:
                        wn += 1
                except IndexError:
                    pass
                except Exception as e:
                    print(f"Unexpected Exception {e} in cg.py checkopen()")
        if wn == 0:
            return 1
        return 0

    def checkn(self, y: int, x: int, n: int) -> int:
        """Return 1 if the neighborhood has more than ``n`` filled tiles."""
        A = self.A
        wn = 0
        for r_x in (-1, 0, 1):
            for r_y in (-1, 0, 1):
                b_x = x + r_x
                b_y = y + r_y
                try:
                    if A[b_y][b_x]:
                        wn += 1
                except IndexError:
                    pass
                except Exception as e:
                    print(f"Unexpected Exception {e} in cg.py checkn()")
        if wn > n:
            return 1
        return 0

    def dprint(self) -> None:
        """Debug print the cave grid."""
        A = self.A
        z = ""
        i = []
        for y in range(self.height):
            for x in range(self.width):
                if A[y][x] == 1:
                    z += "#"
                elif A[y][x] == 3:
                    z += "@"
                else:
                    z += "."
                # z+=str(A[y][x])
            i.append(z)
            z = ""

        for y in range(self.height):
            print(i[y])

    def fix(self) -> None:
        """Add a solid border around the grid."""
        A = self.A
        N = []
        for y in range(self.height + 1):
            lines = []
            for x in range(self.width + 1):
                lines.append(".")
            N.append(lines)

        for y in range(self.height + 1):
            for x in range(self.width + 1):
                if y == 0 or x == 0 or y == self.height - 1 or x == self.width - 1:
                    N[y][x] = 1
                else:
                    N[y][x] = A[y - 1][x - 1]
        self.A = N

    def dget(self) -> list[str]:
        """Return a string representation of the cave grid."""
        A = self.A
        z = ""
        i = []
        for y in range(self.height):
            for x in range(self.width):
                if A[y][x] == 1:
                    z += "#"
                else:
                    z += "."
                # z+=str(A[y][x])
            i.append(z)
            z = ""

        return i
