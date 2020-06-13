import pygame
import random
import sys

pygame.init()
# display window and clock
window = pygame.display.set_mode((1600, 900))
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 98, False, False)
colors = {"red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255)}


# menu items
class MenuItems:
    def __init__(self, length, width):
        self.length = length
        self.width = width
        self.location = (650, 112)
        self.dims = self.length, self.width

    def set_location(self, location):
        self.location = location
        return self.location


bomb = MenuItems(50, 50)
board = MenuItems(672, 672)
miss_marker = MenuItems(83, 83)
hit_marker = MenuItems(83, 83)
enemies = MenuItems(100, 100)
enemy_label = pygame.font.SysFont("arial", 100, False, False)


# Game States
class GameState:
    def __init__(self):
        self.state = False

    def switch_state(self):
        if not self.state:
            self.state = True
        elif self.state:
            self.state = False


start = GameState()
playing = GameState()
lose = GameState()
win_state = GameState()


# Game items
class Bombs:
    def __init__(self, location):
        self.location = location
        self.spent = False

    def shoot_bomb(self):
        self.spent = True

    def draw_bomb(self):
        pygame.draw.rect(window, colors["blue"], (self.location, bomb.dims))

    def draw_x(self):
        if self.spent:
            pygame.draw.line(window, (255, 255, 255), self.location,
                             (self.location[0] + bomb.dims[0], self.location[1] + bomb.dims[1]))
            pygame.draw.line(window, (255, 255, 255), (self.location[0] + bomb.dims[0], self.location[1]),
                             (self.location[0], self.location[1] + bomb.dims[1]))

    def reset_bomb(self):
        self.spent = False

bomb_coordinates = []
for x in range(224, 449, 112):
    for y in range(112, 701, 84):
        bomb_coordinates.append((x, y))
bomb_list = [Bombs(location=xy) for xy in bomb_coordinates]


class Squids:
    def __init__(self, size):
        self.is_dead = False
        self.size = size
        self.spawn_point = []

    def kill(self):
        points = 0
        for space in self.spawn_point:
            if space.hit:
                points += 1
        if points == self.size:
            self.is_dead = True

    def can_spawn(self, conditions):
        if conditions == 4 + self.size:
            return True
        else:
            return False

    def reset_squid(self):
        self.is_dead = False
        self.spawn_point = []


squids = [Squids(l) for l in range(2, 5)]


# Game Spaces
class PlaySpace:
    space_labels = {}
    for x in range(8):
        for y in range(8):
            space_labels[(x + 1, y + 1)] = (651 + (x * 84), 113 + (y * 84))

    def __init__(self, label):
        self.label = label
        self.space = pygame.Rect((self.space_labels[label]), (83, 83))
        self.coords = self.space_labels[label]
        self.is_occupied = False
        self.shot = False
        self.miss = False
        self.hit = False
        self.reveal_win = False
        self.reveal_loss = False

    def occupy_space(self):
        self.is_occupied = True

    def reset(self):
        self.is_occupied = False
        self.shot = False
        self.miss = False
        self.hit = False
        self.reveal_win = False
        self.reveal_loss = False


spaces = [PlaySpace(label=xy) for xy in PlaySpace.space_labels]
space_reference = {}
ref = 0
for x in range(1, 9):
    for y in range(1, 9):
        space_reference[(x, y)] = spaces[ref]
        ref += 1
compass = {"up": -1, "right": 1, "down": 1, "left": -1}


def scan(space, direction, distance):
    if direction == "up" or direction == "down":
        return space_reference[space.label[0], space.label[1] + (compass[direction] * distance)]
    elif direction == "left" or direction == "right":
        return space_reference[space.label[0] + (compass[direction]*distance), space.label[1]]


# Draws game
def draw_lose_screen():
    window.fill((0, 0, 0))
    click = font.render("Click anywhere to play again", True, (255, 255, 255))
    click2 = font.render("or press any key to exit.", True, (255, 255, 255))
    loss_text = font.render("You Lose!", True, (255, 255, 255))
    window.blit(loss_text, (window.get_width()/2 - loss_text.get_width()/2, 250))
    window.blit(click2, (window.get_width()/2 - click2.get_width()/2, 450))
    window.blit(click, (window.get_width()/2 - click.get_width()/2, 350))


def draw_win_screen():
    window.fill((0, 0, 0))
    win_txt = font.render("You killed all the squids!", True, (255, 255, 255))
    click = font.render("Click anywhere to play again", True, (255, 255, 255))
    click2 = font.render("or press any key to exit.", True, (255, 255, 255))
    window.blit(win_txt, (window.get_width() / 2 - win_txt.get_width() / 2, 250))
    window.blit(click2, (window.get_width() / 2 - click2.get_width() / 2, 450))
    window.blit(click, (window.get_width() / 2 - click.get_width() / 2, 350))


def draw_start_screen():
    window.fill((0, 0, 0))
    click = font.render("Click anywhere to begin.", True, (255, 255, 255))
    window.blit(click, (window.get_width() / 2 - click.get_width() / 2, window.get_height()/2 - click.get_height()/2))


def draw_game_screen():
    window.fill((0, 0, 0))
    squid_items = []
    # Draw board and grid
    pygame.draw.rect(window, (128, 128, 128), (board.set_location((650, 112)), board.dims))
    for x in range(board.location[0], board.location[0] + board.length + 1, 84):
        pygame.draw.line(window, (255, 255, 255), (x, board.location[1]), (x, board.location[1] + board.length))
    for y in range(board.location[1], board.location[1] + board.dims[1] + 1, 84):
        pygame.draw.line(window, (255, 255, 255), (board.location[0], y), (board.location[0] + board.width, y))
    # Draw bomb menu item
    for b in bomb_list:
        b.draw_bomb()
        if b.spent:
            b.draw_x()
    # Draw squid menu item
    for y in range(112, 784, 262):
        pygame.draw.rect(window, (255, 0, 0), (enemies.set_location((1388, y)), enemies.dims))
        squid_items.append(enemies.location)
    for num, squid in enumerate(squids):
        window.blit(enemy_label.render(f"{squid.size}", True, (255, 255, 255)),
                    (squid_items[num][0]+25, squid_items[num][1]-6))
    # Draw squid if it died
    for num, squid in enumerate(squids):
        if squid.is_dead:
            pygame.draw.line(window, (255, 255, 255), squid_items[num],
                             (squid_items[num][0] + enemies.dims[0], squid_items[num][1] + enemies.dims[1]-1), 2)
            pygame.draw.line(window, (255, 255, 255), (squid_items[num][0] + enemies.dims[0], squid_items[num][1]),
                             (squid_items[num][0], squid_items[num][1] + enemies.dims[1]-1), 2)
    # Draw Marker if you clicked a space
    for space in spaces:
        if space.shot and space.hit:
            pygame.draw.rect(window, (255, 69, 0), (hit_marker.set_location(space.coords), hit_marker.dims))
        if space.shot and space.miss:
            pygame.draw.rect(window, (0, 0, 255), (hit_marker.set_location(space.coords), hit_marker.dims))
    # Reveal rest of spaces
        if space.reveal_loss:
            pygame.draw.rect(window, (255, 0, 255), (hit_marker.set_location(space.coords), hit_marker.dims))
        if space.reveal_win:
            pygame.draw.rect(window, (0, 255, 255), (hit_marker.set_location(space.coords), hit_marker.dims))



def spawn_squids():
    inverse = {"up": "down",  "down": "up", "left": "right", "right": "left"}
    for squid in squids:
        direction = random.choice(["up", "down", "left", "right"])
        point = random.choice(spaces)
        while point.is_occupied:
            point = random.choice(spaces)
        conditions = 0
        while not squid.can_spawn(conditions):
            conditions = 0
            if direction == "down" and point.label[1] + (squid.size - 1) > 8:
                point = random.choice(spaces)
            else:
                conditions += 1
            if direction == "up" and point.label[1] - (squid.size - 1) < 1:
                point = random.choice(spaces)
            else:
                conditions += 1
            if direction == "right" and point.label[0] + (squid.size - 1) > 8:
                point = random.choice(spaces)
            else:
                conditions += 1
            if direction == "left" and point.label[0] - (squid.size - 1) < 1:
                point = random.choice(spaces)
            else:
                conditions += 1
            for unit in range(squid.size):
                try:
                    if scan(point, direction, unit).is_occupied:
                        point = random.choice(spaces)
                    else:
                        conditions += 1
                except KeyError:
                    print(f"Squid {squid.size} tried to spawn on {point.label} facing {direction}")
        for unit in range(squid.size):
            squid.spawn_point.append(scan(point, direction, unit))
        for space in squid.spawn_point:
            space.occupy_space()


def reset_game():
    for space in spaces:
        space.reset()
    for squid in squids:
        squid.reset_squid()
    for b in bomb_list:
        b.reset_bomb()
    spawn_squids()


def main():
    shots = 0
    pygame.event.set_allowed([pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN, pygame.QUIT])
    spawn_squids()
    start.switch_state()
    for squid in squids:
        space_list = [space.label for space in squid.spawn_point]
        print(f"Squid {squid.size} coordinates: {space_list}")
    while True:
        # Start Screen Game State
        while start.state:
            clock.tick_busy_loop(144)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    start.switch_state()
                    playing.switch_state()
            draw_start_screen()
            pygame.display.update()
        # Game screen for playing game state
        while playing.state:
            clock.tick_busy_loop(144)
            for event in pygame.event.get():
                dead_squids = 0
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.event.clear()
                    for space in spaces:
                        if space.space.collidepoint(pygame.mouse.get_pos()):
                            if not space.shot:
                                space.shot = True
                                try:
                                    bomb_list[shots].shoot_bomb()
                                except IndexError:
                                    bomb_list[23].shoot_bomb()
                                shots += 1
                                if space.is_occupied:
                                    space.hit = True
                                    for squid in squids:
                                        squid.kill()
                                else:
                                    space.miss = True
                                for squid in squids:
                                    if squid.is_dead:
                                        dead_squids += 1
                                # Check to see if game ended
                                if dead_squids == 3:
                                    for squid in squids:
                                        for space in squid.spawn_point:
                                            space.reveal_win = True
                                    draw_game_screen()
                                    pygame.display.update()
                                    reset_game()
                                    pygame.time.delay(2000)
                                    win_state.switch_state()
                                    pygame.event.clear()
                                    playing.switch_state()
                                elif shots == 24:
                                    for squid in squids:
                                        for space in squid.spawn_point:
                                            space.reveal_loss = True
                                    draw_game_screen()
                                    pygame.display.update()
                                    reset_game()
                                    pygame.time.delay(2000)
                                    lose.switch_state()
                                    pygame.event.clear()
                                    playing.switch_state()
            pygame.event.clear()
            draw_game_screen()
            pygame.display.update()
            # game state for loss
            while lose.state:
                shots = 0
                clock.tick_busy_loop(144)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pygame.event.clear()
                        playing.switch_state()
                        lose.switch_state()
                draw_win_screen()
                draw_lose_screen()
                pygame.display.update()
            while win_state.state:
                shots = 0
                clock.tick_busy_loop(144)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pygame.event.clear()
                        playing.switch_state()
                        win_state.switch_state()
                draw_win_screen()
                pygame.display.update()


main()
