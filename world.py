import pygame
import random
import math
pygame.font.init()

class World:
    def __init__(self, seed):
        self.seed = seed
        self.chunks = {}
        self.loaded_chunks = {}
        self.p = PerlinNoise(seed, 256)

    def generate_chunk(self, pos):
        noise_val = self.p.noise(pos[0], pos[1], 256)
        self.chunks[pos] = Chunk(pos[0], pos[1], noise_val)

    def render_world(self, camera):
        r = camera.get_range()  # r = [(x1, y1), (x2, y2)]
        unloaded_chunks = []
        for chunk in self.loaded_chunks:
            pos = self.loaded_chunks[chunk].get_bounds()   # pos = [(x1, y1), (x2, y2)]
            if pos[1][0] < r[0][0] or pos[1][1] < r[0][1] or pos[0][0] > r[1][0] or pos[0][1] > r[1][1]:
                unloaded_chunks.append(chunk)
        for chunk in unloaded_chunks:
            self.loaded_chunks.pop(chunk)
        for pos in [(x, y) for x in range(int(r[0][0] - 1), int(r[1][0] + 1)) for y in range(int(r[0][1] - 1), int(r[1][1] + 1))]:
            if pos not in self.loaded_chunks:
                if pos not in self.chunks:
                    self.generate_chunk(pos)
                self.loaded_chunks[pos] = self.chunks[pos]
        print(f"Chunks rendered: {len(self.loaded_chunks)}")
        for c in self.loaded_chunks:
            camera.render(self.loaded_chunks[c])

class Chunk:

    def __init__(self, x, y, height):
        self.x = x
        self.y = y
        self.height = height
        self.colour = self.calculate_colour_2(height)

    def get_bounds(self):
        pos = [(self.x, self.y), (self.x + 1, self.y + 1)]
        return pos

    def get_colour(self):
        return self.colour

    def calculate_colour_1(self, height):
        c = (255, 255, 255)
        if height < -2:
            c = (79, 66, 181)
        elif height < -0.5:
            c = (0, 128, 255)
        elif height < 0:
            c = (255, 213, 0)
        elif height < 0.85:
            c = (0, 77, 13)
        elif height < 0.9:
            c = (50, 50 ,50)
        elif height < 0.95:
            c = (100, 100, 100)
        return c

    def calculate_colour_2(self, height):
        c = (0, 0, 255 * (height + 1) / 2)
        return c

class Camera:

    DEBUG_FONT = pygame.font.Font('freesansbold.ttf',32)

    def __init__(self, x, y, zoom, win):
        self.zoom = zoom
        self.win = win
        self.win_width = win.get_width()
        self.win_height =  win.get_height()
        self.width = self.win_width / zoom
        self.height = self.win_height / zoom
        self.x = x
        self.y = y
        self.debugging = False

    def get_range(self):
        range = [(self.x - (self.width / 2), self.y - (self.height / 2)), (self.x + (self.width / 2), self.y + (self.height / 2))]
        return range

    def get_screen_rect(self, bounds):
        w = (bounds[1][0] - bounds[0][0]) * self.zoom
        h = (bounds[1][1] - bounds[0][1]) * self.zoom
        x = (-self.x * self.zoom) + ((bounds[0][0] + (self.width / 2)) * self.zoom)
        y = (-self.y * self.zoom) + ((bounds[0][1] + (self.height / 2)) * self.zoom)
        return (x, y, w, h)

    def render(self, obj):
        pygame.draw.rect(self.win, obj.get_colour(), self.get_screen_rect(obj.get_bounds()))
        if self.debugging:
            text = self.DEBUG_FONT.render(f"({round(self.x)}, {round(self.y)}) {self.zoom}", True, (0, 0, 0))
            text_rect = text.get_rect()
            self.win.blit(text, text_rect)

    def zoom_out(self):
        self.zoom = max(self.zoom / 2, 1)
        self.width = self.win_width / self.zoom
        self.height = self.win_height / self.zoom
    
    def zoom_in(self):
        self.zoom = min(self.zoom * 2, 1024)
        self.width = self.win_width / self.zoom
        self.height = self.win_height / self.zoom
    
    def pan(self, pos):
        self.x -= pos[0] / self.zoom
        self.y -= pos[1] / self.zoom

    def toggle_debug(self):
        self.debugging = not self.debugging
        
class PerlinNoise:

    def __init__(self, seed, size):
        random.seed(seed)
        self.gradients = None
        self.permutation_table = None
        self.grid_square = 128
        self.viable_gradients = [self.unit((1, 1)), self.unit((-1, 1)), self.unit((1, -1)), self.unit((-1, -1)), self.unit((2, 0)), self.unit((-2, 0)), self.unit((0, 2)), self.unit((0, -2))]
        self.generate_tables(256)

    def noise(self, x, y, octave):
        gx = (x - (x % octave)) / octave
        gy = (y - (y % octave)) / octave

        x = (x % octave) / octave
        y = (y % octave) / octave

        corners = [(0, 0), (1, 0), (0, 1), (1, 1)]

        gradient_vectors = [ self.gradients[self.get_table_ref((int(gx + corners[i][0]), int(gy + corners[i][1]))) ] for i in range(4) ]
        distance_vectors = [ self.difference(corners[i], (x, y)) for i in range(4) ]
        dot_products = [ self.dot_product(gradient_vectors[i], distance_vectors[i]) for i in range(4) ]

        u = self.smooth(x)
        v = self.smooth(y)

        s = self.lerp(dot_products[0], dot_products[1], u)
        t = self.lerp(dot_products[2], dot_products[3], u)

        height = self.lerp(s, t, v)
        
        return height

    def smooth(self, n):
        return n * n * n * (n * (n * 6 - 15) + 10)

    def difference(self, vector_a, vector_b):
        return (vector_b[0] - vector_a[0], vector_b[1] - vector_a[1])

    def dot_product(self, vector_a, vector_b):
        return (vector_a[0] * vector_b[0]) + (vector_a[1] * vector_b[1])

    def generate_tables(self, size):
        gradients = []
        table = []
        for i in range(size):
            gradients.append(random.choice(self.viable_gradients)) #self.unit((random.randrange(-100, 101), random.randrange(-100, 101))))
            table.append(i)
        random.shuffle(table)
        self.gradients = gradients
        self.permutation_table = table * 2

    def unit(self, v):
        mod_v = math.sqrt((v[0] ** 2) + (v[1] ** 2))
        u = (v[0] / mod_v, v[1] / mod_v)
        return u

    def get_table_ref(self, pos):
        return self.permutation_table[self.permutation_table[pos[0]] + pos[1]]

    def lerp(self, a, b, w):
        return a + w * (b - a)


# random_function(x) such that
# where x = (0, 0) -> f(x) = k
# where x = (5, 0) -> f(x) = n
# where n and k are constants for a given seed]