import os
from random import randrange, choice


class Navigate:  # определение поля
     main = 'User'  # поле кораблей пользователя
     radar = 'AI'  # поля сделанных выстрелов
     weight = 'weight'  # поле весов клеток кораблей


class Cell:  #формы клетки
    empty_cell = 'O'
    ship_cell = '■'
    destroyed_ship = 'X'
    damaged_ship = '□'
    miss_cell = '•'


class Field:
    def __init__(self, size):
        self.size = size
        self.map = [[Cell.empty_cell for _ in range(size)] for _ in range(size)]
        self.radar = [[Cell.empty_cell for _ in range(size)] for _ in range(size)]
        self.weight = [[1 for _ in range(size)] for _ in range(size)]

    def get_field_part(self, element):
        if element == Navigate.main:
            return self.map
        if element == Navigate.radar:
            return self.radar
        if element == Navigate.weight:
            return self.weight

    def draw_field(self, element):  # отрисовка игрового поля
        print('{}'.format(element))
        field = self.get_field_part(element)
        for x in range(-1, self.size):
            for y in range(-1, self.size):
                if x == -1 and y == -1:
                    print("  ", end="")
                    continue
                if x == -1 and y >= 0:
                    print(y + 1, end=" ")
                    continue
                if x >= 0 and y == -1:
                    print(Game.coords[x], end='')
                    continue
                print(" " + str(field[x][y]), end='')
            print("")

    def check_ship_fits(self, ship, element):  #проверка размера корабля относительно поля
        field = self.get_field_part(element)
        x, y = ship.x, ship.y
        width, height = ship.width, ship.height

        if ship.x + ship.height - 1 >= self.size or ship.x < 0 or \
                ship.y + ship.width - 1 >= self.size or ship.y < 0:
           return False

        for pos_x in range(x, x + height):
            for pos_y in range(y, y + width):
                if str(field[pos_x][pos_y]) == Cell.miss_cell:
                    return False

        for pos_x in range(x - 1, x + height + 1):
            for pos_y in range(y - 1, y + width + 1):
                if pos_x < 0 or pos_x >= len(field) or pos_y < 0 or pos_y >= len(field):
                    continue
                if str(field[pos_x][pos_y]) in (Cell.ship_cell, Cell.destroyed_ship):
                    return False

        return True

    def mark_destroyed_ship(self, ship, element):  # определение корабля при попадании
        field = self.get_field_part(element)
        x, y = ship.x, ship.y
        width, height = ship.width, ship.height

        for pos_x in range(x - 1, x + height + 1):
            for pos_y in range(y - 1, y + width + 1):
                if pos_x < 0 or pos_x >= len(field) or pos_y < 0 or pos_y >= len(field):
                    continue
                field[pos_x][pos_y] = Cell.miss_cell

        for pos_x in range(x, x + height):
            for pos_y in range(y, y + width):
                field[pos_x][pos_y] = Cell.destroyed_ship

    def add_ship_to_field(self, ship, element):  #добавление корабля на поле
        field = self.get_field_part(element)
        x, y = ship.x, ship.y
        width, height = ship.width, ship.height

        for pos_x in range(x, x + height):
            for pos_y in range(y, y + width):
                field[pos_x][pos_y] = ship

    def get_max_weight_cells(self):   #определение веса клеток
        weights = {}
        max_weight = 0

        for x in range(self.size):
            for y in range(self.size):
                if self.weight[x][y] > max_weight:
                    max_weight = self.weight[x][y]
                weights.setdefault(self.weight[x][y], []).append((x, y))

        return weights[max_weight]

    def recalculate_weight_map(self, available_ships):  #пересчитывание весов
        self.weight = [[1 for _ in range(self.size)] for _ in range(self.size)]

        for x in range(self.size):
            for y in range(self.size):
                if self.radar[x][y] == Cell.damaged_ship:
                    self.weight[x][y] = 0

                    if x - 1 >= 0:
                        if y - 1 >= 0:
                            self.weight[x - 1][y - 1] = 0
                        self.weight[x - 1][y] *= 50
                        if y + 1 < self.size:
                            self.weight[x - 1][y + 1] = 0

                    if y - 1 >= 0:
                        self.weight[x][y - 1] *= 50
                    if y + 1 < self.size:
                        self.weight[x][y + 1] *= 50

                    if x + 1 < self.size:
                        if y - 1 >= 0:
                            self.weight[x + 1][y - 1] = 0
                        self.weight[x + 1][y] *= 50
                        if y + 1 < self.size:
                            self.weight[x + 1][y + 1] = 0

        for ship_size in available_ships:
            ship = Ship(ship_size, 1, 1, 0)
            for x in range(self.size):
                for y in range(self.size):
                    if self.radar[x][y] in (Cell.destroyed_ship, Cell.damaged_ship, Cell.miss_cell) \
                            or self.weight[x][y] == 0:
                        self.weight[x][y] = 0
                        continue
                    for rotation in range(0, 4):
                        ship.set_position(x, y, rotation)
                        if self.check_ship_fits(ship, Navigate.radar):
                            self.weight[x][y] += 1


class Player(object):
    def __init__(self, name, is_ai):
        self.name = name
        self.is_ai = is_ai
        self.message = []
        self.ships = []
        self.enemy_ships = []
        self.field = None

    def get_input(self, input_type):

        if input_type == "ship_setup":
            user_input = str(choice(Game.coords)) + str(randrange(0, self.field.size)) + choice(["H", "V"])
            x, y, r = user_input[0], user_input[1:-1], user_input[-1]
            return Game.coords.index(x), int(y) - 1, 0 if r == 'H' else 1

        if input_type == "shot":
            if self.is_ai:
                x, y = randrange(0, self.field.size), randrange(0, self.field.size)
            else:
                user_input = input().upper().replace(" ", "")
                x, y = user_input[0].upper(), user_input[1:]
                if x not in Game.coords or not y.isdigit() or int(y) not in range(1, Game.field_size + 1):
                    self.message.append('Data format error')
                    return 500, 0
                x = Game.coords.index(x)
                y = int(y) - 1
            return x, y

    def make_shot(self, target_player):

        sx, sy = self.get_input('shot')

        if sx + sy == 500 or self.field.radar[sx][sy] != Cell.empty_cell:
            return 'retry'

        shot_res = target_player.receive_shot((sx, sy))

        if shot_res == 'miss':
            self.field.radar[sx][sy] = Cell.miss_cell

        if shot_res == 'get':
            self.field.radar[sx][sy] = Cell.damaged_ship

        if type(shot_res) == Ship:
            destroyed_ship = shot_res
            self.field.mark_destroyed_ship(destroyed_ship, Navigate.radar)
            self.enemy_ships.remove(destroyed_ship.size)
            shot_res = 'kill'

        self.field.recalculate_weight_map(self.enemy_ships)

        return shot_res

    def receive_shot(self, shot):

        sx, sy = shot

        if type(self.field.map[sx][sy]) == Ship:
            ship = self.field.map[sx][sy]
            ship.hp -= 1

            if ship.hp <= 0:
                self.field.mark_destroyed_ship(ship, Navigate.main)
                self.ships.remove(ship)
                return ship

            self.field.map[sx][sy] = Cell.damaged_ship
            return 'get'

        else:
            self.field.map[sx][sy] = Cell.miss_cell
            return 'miss'


class Ship:

    def __init__(self, size, x, y, rotation):

        self.size = size
        self.hp = size
        self.x = x
        self.y = y
        self.rotation = rotation
        self.set_rotation(rotation)

    def __str__(self):
        return Cell.ship_cell

    def set_position(self, x, y, r):
        self.x = x
        self.y = y
        self.set_rotation(r)

    def set_rotation(self, r):

        self.rotation = r

        if self.rotation == 0:
            self.width = self.size
            self.height = 1
        elif self.rotation == 1:
            self.width = 1
            self.height = self.size
        elif self.rotation == 2:
            self.y = self.y - self.size + 1
            self.width = self.size
            self.height = 1
        elif self.rotation == 3:
            self.x = self.x - self.size + 1
            self.width = 1
            self.height = self.size


class Game(object):
    coords = ("1", "2", "3", "4", "5", "6")
    list_of_ships = [1, 1, 1, 2, 2, 4]
    field_size = len(coords)

    def __init__(self):

        self.players = []
        self.current_player = None
        self.next_player = None
        self.status = 'prepare'

    def start_game(self):
        self.current_player = self.players[0]
        self.next_player = self.players[1]

    def status_check(self):
        if self.status == 'prepare' and len(self.players) >= 2:
            self.status = 'in game'
            self.start_game()
            return True
        if self.status == 'in game' and len(self.next_player.ships) == 0:
            self.status = 'game over'
            return True

    def add_player(self, player):
        player.field = Field(Game.field_size)
        player.enemy_ships = list(Game.list_of_ships)
        self.ships_setup(player)
        player.field.recalculate_weight_map(player.enemy_ships)
        self.players.append(player)

    def ships_setup(self, player):
        for ship_size in Game.list_of_ships:
            retry_count = 20
            ship = Ship(ship_size, 0, 0, 0)
            while True:
                Game.clear_screen()
                print('{}. We arrange ships ...'.format(player.name))
                player.message.clear()

                x, y, r = player.get_input('ship_setup')
                if x + y + r == 0:
                    continue
                ship.set_position(x, y, r)
                if player.field.check_ship_fits(ship, Navigate.main):
                    player.field.add_ship_to_field(ship, Navigate.main)
                    player.ships.append(ship)
                    break

                retry_count -= 1
                if retry_count < 0:
                    player.field.map = [[Cell.empty_cell for _ in range(Game.field_size)] for _ in
                                        range(Game.field_size)]
                    player.ships = []
                    self.ships_setup(player)
                    return True

    def draw(self):
        if not self.current_player.is_ai:
            self.current_player.field.draw_field(Navigate.main)
            self.current_player.field.draw_field(Navigate.radar)
        for line in self.current_player.message:
            print(line)

    def switch_players(self):
        self.current_player, self.next_player = self.next_player, self.current_player

    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    def gameloop(self):
        players = []
        players.append(Player(name='User', is_ai=False))
        players.append(Player(name='AI', is_ai=True))

        game = Game()

        while True:
            game.status_check()
            self.invite()
            if game.status == 'prepare':
                game.add_player(players.pop(0))

            if game.status == 'in game':
                Game.clear_screen()
                game.current_player.message.append("Your move: ")
                game.draw()
                game.current_player.message.clear()
                shot_result = game.current_player.make_shot(game.next_player)
                if shot_result == 'miss':
                    game.next_player.message.append('{} miss! '.format(game.current_player.name))
                    game.next_player.message.append('Your move {}:!'.format(game.next_player.name))
                    game.switch_players()
                    continue
                elif shot_result == 'retry':
                    game.current_player.message.append('Retry!')
                    continue
                elif shot_result == 'get':
                    game.current_player.message.append('Damage, your next move!')
                    game.next_player.message.append('Our ship came under fire!')
                    continue
                elif shot_result == 'kill':
                    game.current_player.message.append('Enemy ship is destroyed!')
                    game.next_player.message.append('User ship is destroyed')
                    continue

            if game.status == 'game over':
                Game.clear_screen()
                game.next_player.field.draw_field(Navigate.main)
                game.current_player.field.draw_field(Navigate.main)
                print('It`s the last ship {}'.format(game.next_player.name))
                print('{} win! Congratulations'.format(game.current_player.name))
                if self.play_again():
                    self.clear_screen()
                    self.gameloop()
                else:
                    break

        print('Thanks for a game!')
        input('')

    def invite(self):
        print('-'*30)
        print('BattleShip'.center(30))

    def play_again(self):
        print('Хотите сыграть еще? (да или нет)')
        return input().lower().startswith('д')


    def start(self):
        self.gameloop()


g = Game()
g.start()
