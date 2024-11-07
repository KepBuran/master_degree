import math
import random
import numpy as np

from grid.grid import Grid

class GridGenerator:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.grid = None


    def generate_grid(self, cell_size): 
        return self.generate_grid_sizes(cell_size).generate_growth_grid().grid 

    def generate_grid_sizes(self, cell_size):
        x_offset = random.uniform(0, 0.2) * self.screen_width
        y_offset = random.uniform(0, 0.2) * self.screen_height

        grid_width = random.uniform(0.6, 0.8) * self.screen_width
        grid_height = random.uniform(0.6, 0.8) * self.screen_height

        self.grid = Grid(cell_size, math.floor(grid_width / cell_size) * cell_size, math.floor(grid_height / cell_size) * cell_size, x_offset, y_offset)

        return self
    
    def bresenham_line(self, x0, y0, x1, y1):
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            points.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

        return points
    
    def rotate_point(self, x, y, angle):
        """Rotate a point (x, y) around the origin by the given angle."""
        cos_theta = math.cos(angle)
        sin_theta = math.sin(angle)
        return (x * cos_theta - y * sin_theta, x * sin_theta + y * cos_theta)

    def generate_line(self, growth_grid):
        if (not self.grid):
            print("You need to generate grid sizes first")
            return
        
        grid_width = len(self.grid.grid[0])
        grid_height = len(self.grid.grid)
        
        min_distance = 0.3 * min(grid_width, grid_height)
        
        # Take two random points in the grid with distance between them from 100% to 30% of the grid size
        while True:
            y1, x1 = random.randint(0, grid_width - 1), random.randint(0, grid_height - 1)
            y2, x2 = random.randint(0, grid_width - 1), random.randint(0, grid_height - 1)
            
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            
            if min_distance <= distance:
                break

        width = random.randint(2, 5)
        growth = random.randint(2, 4)

        # # Make straight line between two points with given width and growth

         # Calculate the angle of the line
        dx = x2 - x1
        dy = y2 - y1
        angle = math.atan2(dy, dx)

        # Half-width offset perpendicular to the line
        perpendicular_angle = angle + math.pi / 2
        half_width = math.floor((width - 1) / 2)

        # Collect points that shouldn't be modified twice
        modified_points = set()

        offset_x, offset_y = self.rotate_point(1, 0, perpendicular_angle)
        offset_x, offset_y = int(round(offset_x)), int(round(offset_y))

        # Make sure that only one of offsets is 1
        if offset_x != 0 and offset_y != 0:
            offset_x = 1
            offset_y = 0

        # Get the points for the line
        line_points = self.bresenham_line(x1, y1, x2, y2)
        
        # Modify the growth_grid only at unique points
        for x, y in line_points:
            for i in range(-half_width, half_width + 1):
                x_with_offset = x + offset_x * i
                y_with_offset = y + offset_y * i
                if 0 <= x_with_offset < len(growth_grid) and 0 <= y_with_offset < len(growth_grid[0]):
                    if (x_with_offset, y_with_offset) not in modified_points:
                        growth_grid[x_with_offset][y_with_offset] = growth
                        modified_points.add((x_with_offset, y_with_offset))


        return growth_grid


    def generate_ellipse(self, growth_grid):
        # Take random point in the grid
        x1, y1 = random.randint(0, len(growth_grid[0]) - 1), random.randint(0, len(growth_grid) - 1)

        # Take random offset for the second point
        offset_x, offset_y = random.randint(4, 10), random.randint(4, 10)

        # Calculate the second point
        while True:
            x2, y2 = x1 + offset_x, y1 + offset_y
            if 0 <= x2 < len(growth_grid[0]) and 0 <= y2 < len(growth_grid) and x1 != x2 and y1 != y2:
                break
            offset_x, offset_y = random.randint(4, 10), random.randint(4, 10)

        growth_value = random.randint(2, 4)

        # Convert points to numpy arrays for easier calculations
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # Calculate the axes lengths based on the distance between the points
        a = abs(x2 - x1) / 2
        b = abs(y2 - y1) / 2
        
        rows = len(growth_grid)
        cols = len(growth_grid[0])
        
        # Iterate through each cell in the growth_grid
        for i in range(rows):
            for j in range(cols):
                # Check if the point (i, j) is within the ellipse
                if ((i - center_y)**2) / (b**2) + ((j - center_x)**2) / (a**2) <= 1:
                    growth_grid[i][j] += growth_value

        return growth_grid
    
    def generate_circle(self, growth_grid):
        # Take random point in the grid
        x1, y1 = random.randint(0, len(growth_grid[0]) - 1), random.randint(0, len(growth_grid) - 1)

        radius = random.randint(3, 8)
        growth_value = random.randint(2, 4)

        rows = len(growth_grid)
        cols = len(growth_grid[0])

        # Calculate the bounding box for the circle
        x_min = max(0, x1 - radius)
        x_max = min(cols - 1, x1 + radius)
        y_min = max(0, y1 - radius)
        y_max = min(rows - 1, y1 + radius)

        # Iterate through each cell in the bounding box
        for i in range(y_min, y_max + 1):
            for j in range(x_min, x_max + 1):
                # Check if the point (i, j) is within the circle
                if (i - y1)**2 + (j - x1)**2 <= radius**2:
                    growth_grid[i][j] += growth_value

        return growth_grid
    
    def generate_growth_grid(self):
        if (not self.grid):
            print("You need to generate grid sizes first")
            return
        
        growth_grid = self.grid.growth_grid.copy()

        amount_of_lines = random.randint(4, 4)
        for _ in range(amount_of_lines):
            growth_grid = self.generate_line(growth_grid)  

        amount_of_ellipses = random.randint(4, 5)
        for _ in range(amount_of_ellipses):
            growth_grid = self.generate_ellipse(growth_grid)

        amount_of_circles = random.randint(2, 3)
        for _ in range(amount_of_circles):
            growth_grid = self.generate_circle(growth_grid)

        self.grid.growth_grid = growth_grid
        self.grid.grid = growth_grid.copy()

        return self
        