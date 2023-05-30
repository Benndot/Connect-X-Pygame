import sys
import pygame
from pygame import mixer
import random
import math
from dataclasses import dataclass
import numpy as np
import shelve
import music_settings as music

# ----------------------------------------------------------------------------------------------------------------------
# Initializing pygame, saves, music settings, etc.

pygame.init()
clock = pygame.time.Clock()

save_file = shelve.open("save_file1")

mixer.init()
music_object = music.MusicSettings()
music_object.randomize_song()


# ----------------------------------------------------------------------------------------------------------------------
# Save game utility functions


def var_save_value(file, key_name, fallback):
    # Use this for plain variables, just a dumb system that handles errors
    while True:
        try:
            return file[key_name]
        except KeyError:
            print(f"SAVE file or key does not exist. Setting value to {fallback}")
            return fallback


def obtain_save_value(file, obj):
    # Determines via the persistent data saved to shelve file what a given Stat object's saved value is

    # Maybe we could save custom game modes using this?
    if type(obj).__name__ == "Stat":
        while True:
            try:
                return file[obj.name]
            except KeyError:
                print(f"SAVE file or key does not exist. Setting value to 0 (default)")
                return 0

    if type(obj).__name__ == "Replay":
        while True:
            try:
                return file[obj.id]
            except KeyError:
                print(f"SAVE file or key does not exist. Setting replay values to defaults.")
                return Replay(obj.id, "Replay", tic_tac_toe, [], [], True, "X", "O")

    if type(obj).__name__ == "GameMode":
        while True:
            try:
                return file["custom_mode"]
            except KeyError:
                print(f"SAVE file or key does not exist. Setting custom mode values to defaults.")
                return GameMode("Custom", np.full((99, 99), "-"), 99)


class GameScreen:
    width = 1080
    height = 720
    screen = pygame.display.set_mode((width, height))

    def resize_screen(self):
        if self.width == 1080:
            self.width = 1600
            self.height = 900
            self.screen = pygame.display.set_mode((self.width, self.height))
        elif self.width == 1600:
            self.width = 1920
            self.height = 1080
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        else:
            self.width = 1080
            self.height = 720
            self.screen = pygame.display.set_mode((self.width, self.height))


game_screen = GameScreen()
pygame.display.set_caption("Benndot's Connect X")
connect_icon = pygame.image.load("images/connect.png")
pygame.display.set_icon(connect_icon)

# Setting different sized font options to be used later for general text and button labels
xxl_font = pygame.font.SysFont("comicsansms", math.ceil(game_screen.height * 0.0695 * 1.4))
xl_font = pygame.font.SysFont("comicsansms", math.ceil(game_screen.height * 0.0695 * 1.2))
large_font = pygame.font.SysFont("comicsansms", math.ceil(game_screen.height * 0.0695))
intermediate_font = pygame.font.SysFont("comicsansms", math.ceil(game_screen.height * 0.0695 * 0.8))
medium_font = pygame.font.SysFont("comicsansms", math.ceil(game_screen.height * 0.0695 * 0.6))
sml_med_font = pygame.font.SysFont("comicsansms", math.ceil(game_screen.height * 0.0695 * 0.45))
small_font = pygame.font.SysFont("comicsansms", math.ceil(game_screen.height * 0.0695 * 0.33))

# Establishing a number of reusable rgb values for several colors
slategray = (112, 128, 144)
lightgray = (165, 175, 185)
blackish = (20, 20, 20)
thunderbird_red = (200, 15, 25)
white = (255, 255, 255)
red = (255, 0, 0)
lighter_red = (180, 0, 0)
green = (0, 255, 0)
lighter_green = (0, 180, 0)
thistle_green = (210, 210, 190)
black = (0, 0, 0)


def create_onscreen_text(font_size, color, message, x, y, x_adjust: bool = False):

    text = font_size.render(message, True, color)

    if x_adjust:
        text_width = text.get_width()
        x = x - (text_width / 2)

    game_screen.screen.blit(text, (x, y))


def display_text_over_multiple_lines(text, font, line_character_limit, start_x, start_y, line_height_step):
    start_index = 0
    height_multiplier = 1
    index_counter = 0
    for index, char in enumerate(text):
        index_counter += 1
        if char == " " and index_counter >= line_character_limit:
            end_index = index + 1
            create_onscreen_text(font, black, text[start_index: end_index], start_x, start_y * height_multiplier, False)
            height_multiplier += line_height_step
            start_index = index
            index_counter = 0
        if index >= len(text) - 1:
            create_onscreen_text(font, black, text[start_index: -1], start_x, start_y * height_multiplier, False)
            break


def create_transparent_button(width, height, x, y):

    mouse = pygame.mouse.get_pos()

    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        s = pygame.Surface((width, height))  # the size of your rect
        s.set_alpha(128)  # alpha level
        s.fill((255, 255, 255))  # this fills the entire surface
        game_screen.screen.blit(s, (x, y))  # (0,0) are the top-left coordinates
        for evnt in pygame.event.get():
            if evnt.type == pygame.MOUSEBUTTONUP:
                return True


def create_text_button(font_choice, text_color, msg, x, y, hover_color, default_color, x_adjust: bool,
                       click_sound: bool = True):

    mouse = pygame.mouse.get_pos()

    button_msg = font_choice.render(msg, True, text_color)

    button_width = button_msg.get_width() + (button_msg.get_width() * 0.20)
    button_height = button_msg.get_height() + (button_msg.get_height() * 0.20)

    if x_adjust:
        x = x - (button_width / 2)

    # The experimental version
    if x + button_width > mouse[0] > x and y + button_height > mouse[1] > y:
        pygame.draw.rect(game_screen.screen, hover_color, (x, y, button_width, button_height))
        for evnt in pygame.event.get():
            if evnt.type == pygame.MOUSEBUTTONUP:
                if click_sound:
                    button_effect = mixer.Sound('audio/click_v2.mp3')
                    mixer.Sound.play(button_effect)
                return True
    else:
        pygame.draw.rect(game_screen.screen, default_color, (x, y, button_width, button_height))

    game_screen.screen.blit(button_msg, (x + button_width / 10, y + button_height / 10))


# ----------------------------------------------------------------------------------------------------------------------
# 3. Defining the GameMode class and creating several instances representing a variety of playable game modes


@dataclass()
class GameMode:
    title: str  # The name of the game mode
    board: np.ndarray  # The arrangement/dimensions of the game board_shape
    objective: int  # The number of consecutive characters needed to win
    cell_width: float = float(game_screen.width / 10)
    cell_height: float = float(game_screen.height / 7)
    cell_x_offset: float = float(0.15)  # A multiplier for determining a cell's generated position
    cell_y_offset: float = float(0.12)  # A multiplier for determining a cell's generated position
    x_offset_step: float = float(0.1)  # The space multiplier that separates each cell as they're generated
    y_offset_step: float = float(0.15)
    font: pygame.font = large_font


connect4 = GameMode("Connect4", np.full((6, 7), "-"), 4, cell_width=float(game_screen.width / 11),
                    cell_height=float(game_screen.height / 8), x_offset_step=float(0.095),
                    y_offset_step=float(0.125), cell_x_offset=float(0.17))

connect3 = GameMode("Connect3", np.full((4, 5), "-"), 3, cell_width=float(game_screen.width / 8.5),
                    cell_height=float(game_screen.height / 6.5), x_offset_step=float(0.12),
                    y_offset_step=float(0.16), cell_x_offset=float(0.2))

wide_boi = GameMode("Wide Boi", np.full((4, 8), "-"), 4)

tall_boi = GameMode("Tall Boi", np.full((8, 4), "-"), 4)

tic_tac_toe = GameMode("Tic-Tac-Toe", np.full((3, 3), "-"), 3, cell_width=float(game_screen.width / 6.5),
                       cell_height=float(game_screen.height / 5), x_offset_step=float(0.16),
                       y_offset_step=float(0.22), cell_x_offset=float(0.24),
                       font=xl_font)

cheese_crackers = GameMode("Cheese & Crackers", np.full((5, 5), "-"), 4)

deluxe = GameMode("Connect6", np.full((9, 10), "-"), 6)

custom_mode = GameMode("Custom", np.full((99, 99), "-"), 99)  # Not meant to be played in this form


# ----------------------------------------------------------------------------------------------------------------------
# 4. DEFINING THE STAT CLASS AND THE REPLAY CLASS TO TRACK IN-GAME HISTORY


@dataclass()
class Stat:
    name: str  # The name of the stat in question
    value: int  # the value of that statistic


@dataclass()
class Replay:
    id: int  # Unchanging unique identifier for each replay instance
    name: str  # Name of the replay, can be edited by the user
    game_mode: GameMode  # In which game mode did the game take place
    player_moves: list  # The sequence of moves that the player made
    enemy_moves: list  # The sequence of moves that the enemy made
    priority: bool  # Whether player had the priority in the game or not
    player_symbol: str
    enemy_symbol: str

    def __str__(self):
        return f"Replay: {self.name}, Mode: {self.game_mode.title}, Turns: " \
               f"{len(self.player_moves) if len(self.player_moves) >= len(self.enemy_moves) else len(self.enemy_moves)}"


class ReplayManager:
    r1 = Replay(1, "Empty", tic_tac_toe, [], [], True, "X", "O")
    r2 = Replay(2, "Empty", tic_tac_toe, [], [], True, "X", "O")
    r3 = Replay(3, "Empty", tic_tac_toe, [], [], True, "X", "O")
    r4 = Replay(4, "Empty", tic_tac_toe, [], [], True, "X", "O")
    r5 = Replay(5, "Empty", tic_tac_toe, [], [], True, "X", "O")

    replay_list = [r1, r2, r3, r4, r5]


# ----------------------------------------------------------------------------------------------------------------------
# 5. DEFINING GLOBAL VARIABLES


class DataTracker:

    wins = Stat("Wins", 0)
    losses = Stat("Losses", 0)
    ties = Stat("Ties", 0)

    # These two lists will track the list of all moves the player and CPU make, to be pushed if a replay is saved
    player_move_list: list = []
    enemy_move_list: list = []

    # Variable controlling whether to ask if the rules should be explained
    rule_toggle: bool = True


class GameHandler:

    current_mode = connect4

    difficulty: int = 80  # Setting a CPU difficulty level variable

    player_symbol: str = var_save_value(save_file, "player_symbol", "X")
    enemy_symbol: str = var_save_value(save_file, "enemy_symbol", "O")

    priority: bool = True  # Who goes/went first in a given game
    player_turn = True

    enemy_turn_length = 3500  # in milliseconds
    enemy_turn_start_time = 1  # Will contain the pygame.time.getticks() of when the CPU's turn began
    time_taken = False  # Bool to show that the enemy_turn_start_time was taken

    game_status: str = "pregame"  # Options are pregame, ongoing, won, lost, tied


# ----------------------------------------------------------------------------------------------------------------------
# 6. Initializing all shelved save data that the game tracks between sessions

# Currently nothing to be saved, as save-data is not implemented in this project yet.

# ----------------------------------------------------------------------------------------------------------------------
# 8. Menu, game mode selection (and creation), and board_shape display functions


def title_screen():

    title_image = pygame.image.load("images/connect4-board-pic.jpg")

    nav_bar_height = game_screen.height / 7

    # Scales the start screen image to the screen size
    title_image = pygame.transform.scale(title_image, (game_screen.width, game_screen.height - (game_screen.height / 10)
                                                       ))

    while True:
        game_screen.screen.fill((0, 0, 200))

        create_onscreen_text(intermediate_font, white, "Connect X", game_screen.width / 2, game_screen.height / 90,
                             True)
        create_onscreen_text(medium_font, white, "by Benndot", game_screen.width / 2, game_screen.height / 13,
                             True)

        start_button = create_text_button(medium_font, black, "Start", game_screen.width * .15, game_screen.height *
                                          0.02, green, lighter_green, True)

        if start_button:
            main_menu()

        options_button = create_text_button(medium_font, black, "Options", game_screen.width * .8,
                                            game_screen.height * 0.02, (200, 200, 0), (120, 120, 0), True)

        if options_button:
            sound_menu()

        music_button = create_text_button(small_font, blackish, "Toggle Music", game_screen.width * .925,
                                          game_screen.height * 0.035, lightgray, slategray, True)

        if music_button:
            music_object.music_toggle()

        game_screen.screen.blit(title_image, (0, nav_bar_height))

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(15)


def main_menu():

    greeting_message = "Main Menu"

    play_game_str = {"Play": mode_selection}
    change_symbol_str = {"Change Symbol": symbol_selection}
    stats_replays_str = {"Replays": replays_menu}
    audio_options = {"Audio Options": sound_menu}
    save_options_str = {"Save File Options": save_settings}
    quit_game_str = {"Quit": sys.exit}

    menu_options = [play_game_str, change_symbol_str, stats_replays_str, audio_options, save_options_str, quit_game_str]

    while True:

        game_screen.screen.fill((230, 60, 160))

        create_onscreen_text(large_font, black, greeting_message, game_screen.width / 2, game_screen.height * 0.05,
                             True)

        create_onscreen_text(medium_font, black, f"Wins: {DataTracker.wins.value}", game_screen.width / 15,
                             game_screen.height * 0.9)
        create_onscreen_text(medium_font, black, f"Losses: {DataTracker.losses.value}", game_screen.width / 2.25,
                             game_screen.height * 0.9)
        create_onscreen_text(medium_font, black, f"Ties: {DataTracker.ties.value}", game_screen.width / 1.2,
                             game_screen.height * 0.9)

        base_height = game_screen.height * 0.25
        height_multiplier = 1
        for index, option in enumerate(menu_options, 1):
            button = create_text_button(medium_font, white, f"{index}. {list(option.keys())[0]}", game_screen.width / 4,
                                        base_height * height_multiplier, lighter_green, green, False)
            if button:
                option.get(list(option.keys())[0])()

            height_multiplier += 0.4

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(15)


def replays_menu():

    delete_option: bool = False

    while True:

        game_screen.screen.fill((30, 105, 230))

        create_onscreen_text(large_font, black, "Replays Menu", game_screen.width / 2, game_screen.height * 0.05, True)

        height_multiplier = 1
        for replay in ReplayManager.replay_list:
            replay_button = create_text_button(medium_font, black, replay.__str__(), game_screen.width / 2,
                                               game_screen.height * 0.25 * height_multiplier, lightgray, slategray,
                                               True, False)

            if replay_button:
                if replay.name != "Empty":
                    button_click = mixer.Sound("audio/button_click.mp3")
                    mixer.Sound.play(button_click)
                    replay_player(replay)
                else:
                    denial_sound = mixer.Sound("audio/rejection.wav")
                    mixer.Sound.play(denial_sound)

            if delete_option:
                delete_button = create_text_button(medium_font, black, "X", game_screen.width * 0.88,
                                                   game_screen.height * 0.25 * height_multiplier, red, lightgray,
                                                   True, False)

                if delete_button:
                    replay.name = "Empty"
                    replay.game_mode = tic_tac_toe
                    replay.player_moves = []
                    replay.enemy_moves = []
                    replay.priority = False
                    replay.player_symbol = "X"
                    replay.enemy_symbol = "O"
                    print("Replay deleted!")

            height_multiplier += 0.35

        del_options_button = create_text_button(medium_font, black, "Delete Replays?", game_screen.width / 2,
                                                game_screen.height * 0.85, slategray, lightgray, True)

        if del_options_button:
            delete_option = not delete_option

        return_button = create_text_button(medium_font, black, "Return", game_screen.width / 1.2,
                                           game_screen.height * 0.85, slategray, lightgray, False, True)

        if return_button:
            main_menu()

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(15)


def replay_player(replay):
    def cycle_turn(participant: str):

        if participant == "player":
            try:
                move_coords = replay.player_moves[move_list_index]
                grid_manager.grid[move_coords[0]][move_coords[1]].value = replay.player_symbol
            except IndexError:
                print("Move does not exist")
                return True

        if participant == "enemy":
            try:
                move_coords = replay.enemy_moves[move_list_index]
                grid_manager.grid[move_coords[0]][move_coords[1]].value = replay.enemy_symbol
            except IndexError:
                print("Move does not exist")
                return True
        return False

    move_list_index = 0  # This is the proper index of the current turn

    grid_manager.generate_replay_grid(replay)  # Setting up the grid

    replay_complete = False  # True if we have reached the end of one of the move lists

    turn_timer_gate: bool = False
    turn_timer_start: int = 0

    while True:

        game_screen.screen.fill((210, 90, 55))

        header_string = "Start" if move_list_index == 0 else f"Turn {move_list_index}" if not replay_complete \
            else f"Complete"
        create_onscreen_text(large_font, black, header_string, game_screen.width / 2, game_screen.height / 50, True)

        create_onscreen_text(medium_font, black, "Player", game_screen.width * 0.05, game_screen.height * 0.25)
        create_onscreen_text(medium_font, black, f"{replay.player_symbol}", game_screen.width * 0.05,
                             game_screen.height * 0.32)
        create_onscreen_text(medium_font, black, "CPU", game_screen.width * 0.05, game_screen.height * 0.42)
        create_onscreen_text(medium_font, black, f"{replay.enemy_symbol}", game_screen.width * 0.05,
                             game_screen.height * 0.50)

        grid_manager.blit_grid()

        progress_button = create_text_button(intermediate_font, black if not turn_timer_gate else white,
                                             "Progress", game_screen.width / 2, game_screen.height * 0.88,
                                             slategray if not turn_timer_gate else black,
                                             lightgray if not turn_timer_gate else black,
                                             True,
                                             True if not turn_timer_gate else False)

        if progress_button and not turn_timer_gate:
            print("Progress game replay 1 turn")
            replay_complete = cycle_turn('player') if replay.priority else cycle_turn('enemy')
            turn_timer_gate = True
            turn_timer_start = pygame.time.get_ticks()

        current_time = pygame.time.get_ticks()
        if turn_timer_gate and current_time - turn_timer_start >= 1000:
            replay_complete = cycle_turn('enemy') if replay.priority else cycle_turn('player')
            turn_timer_gate = False
            move_list_index += 1

        reset_button = create_text_button(medium_font, black, "Reset", game_screen.width / 65,
                                          game_screen.height * 0.88, slategray, lightgray, False, True)

        if reset_button:
            print("Reset")
            grid_manager.grid = []
            grid_manager.generate_replay_grid(replay)
            move_list_index = 0
            replay_complete = False
            turn_timer_gate: bool = False
            turn_timer_start: int = 0

        return_button = create_text_button(medium_font, black, "Return", game_screen.width / 1.18,
                                           game_screen.height * 0.88, slategray, lightgray, False, True)

        if return_button:
            grid_manager.grid = []  # Resetting the grid state
            main_menu()

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(15)


def symbol_selection():

    player_symbol_var = f"{GameHandler.player_symbol}"  # Empty string that will hold the user's input
    player_box_active = False
    player_var_x = game_screen.width * 0.28

    var_y = game_screen.height * 0.4

    enemy_symbol_var = f"{GameHandler.enemy_symbol}"  # Empty string that will hold the user's input
    enemy_box_active = False
    enemy_var_x = game_screen.width * 0.68

    example_surface = xl_font.render("A", True, black)

    while True:

        game_screen.screen.fill((55, 195, 120))

        create_onscreen_text(large_font, black, "Symbol Select", game_screen.width / 2, game_screen.height * 0.05, True)

        create_onscreen_text(medium_font, black, "Player", player_var_x * 0.96, game_screen.height * 0.3)
        create_onscreen_text(medium_font, black, "CPU", enemy_var_x * 0.99, game_screen.height * 0.3)

        create_onscreen_text(xl_font, black, player_symbol_var, player_var_x, var_y)
        create_onscreen_text(xl_font, black, enemy_symbol_var, enemy_var_x, var_y)

        player_box_border = pygame.Rect(player_var_x - (game_screen.height / 72), var_y, example_surface.get_width() +
                                        24, example_surface.get_height() + 16)
        enemy_box_border = pygame.Rect(enemy_var_x - (game_screen.height / 72), var_y, example_surface.get_width() +
                                       24, example_surface.get_height() + 16)

        return_button = create_text_button(medium_font, black, "main menu", game_screen.width / 2,
                                           game_screen.height * 0.8, slategray, lightgray, True)

        if return_button:
            main_menu()

        submit_button = create_text_button(medium_font, black, "confirm", game_screen.width / 2,
                                           game_screen.height * 0.6, slategray, lightgray, True)

        if submit_button:
            if player_symbol_var != enemy_symbol_var:
                if len(player_symbol_var) == 1 and player_symbol_var != GameHandler.player_symbol:
                    GameHandler.player_symbol = player_symbol_var
                if len(enemy_symbol_var) == 1 and enemy_symbol_var != GameHandler.enemy_symbol:
                    GameHandler.enemy_symbol = enemy_symbol_var

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evnt.type == pygame.MOUSEBUTTONDOWN:
                if player_box_border.collidepoint(evnt.pos):
                    player_box_active = not player_box_active
                    if player_box_active and enemy_box_active:
                        enemy_box_active = not enemy_box_active
                if enemy_box_border.collidepoint(evnt.pos):
                    enemy_box_active = not enemy_box_active
                    if enemy_box_active and player_box_active:
                        player_box_active = not player_box_active
                if not player_box_border.collidepoint(evnt.pos) and not enemy_box_border.collidepoint(evnt.pos):
                    if enemy_box_active:
                        enemy_box_active = not enemy_box_active
                    if player_box_active:
                        player_box_active = not player_box_active

            if evnt.type == pygame.KEYDOWN:

                if player_box_active:
                    if evnt.key == pygame.K_BACKSPACE:
                        player_symbol_var = ""
                    else:
                        player_symbol_var = evnt.unicode

                if enemy_box_active:
                    if evnt.key == pygame.K_BACKSPACE:
                        enemy_symbol_var = ""
                    else:
                        enemy_symbol_var = evnt.unicode

        if player_box_active:
            pygame.draw.rect(game_screen.screen, white, player_box_border, 2)
        else:
            pygame.draw.rect(game_screen.screen, slategray, player_box_border, 2)

        if enemy_box_active:
            pygame.draw.rect(game_screen.screen, white, enemy_box_border, 2)
        else:
            pygame.draw.rect(game_screen.screen, slategray, enemy_box_border, 2)

        pygame.display.update()
        clock.tick(15)


def save_settings():

    header_message = "Save Settings"

    greeting = "Go Away"

    while True:

        game_screen.screen.fill((85, 165, 180))

        create_onscreen_text(large_font, black, header_message, game_screen.width / 2, game_screen.height * 0.05, True)
        create_onscreen_text(large_font, black, greeting, game_screen.width / 2, game_screen.height * 0.20, True)

        return_button = create_text_button(medium_font, black, "main menu", game_screen.width / 2,
                                           game_screen.height * 0.5, slategray, lightgray, True)

        if return_button:
            main_menu()

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(15)


def sound_menu():

    title_text = large_font.render("Options Menu", True, blackish)

    volume_controls_height = game_screen.height / 2.8

    while True:
        game_screen.screen.fill(thistle_green)
        game_screen.screen.blit(title_text, ((game_screen.width - title_text.get_width()) / 2, 0))

        music_button = create_text_button(medium_font, white, "Toggle Music", game_screen.width / 1.97,
                                          game_screen.height / 6.5, lightgray, slategray, True)
        if music_button:
            music_object.music_toggle()

        music_pause_declaration = "Yes" if music_object.music_paused else "No"
        create_onscreen_text(medium_font, black, f"Music Paused: " + music_pause_declaration, game_screen.width / 2,
                             game_screen.height / 3.8, True)

        create_onscreen_text(medium_font, black, f"{music_object.volume_level}", game_screen.width / 2,
                             volume_controls_height - 15, True)

        volume_up_button = create_text_button(small_font, white, "Volume +", game_screen.width / 2.3,
                                              volume_controls_height, slategray, lightgray, True)

        volume_down_button = create_text_button(small_font, white, "Volume -", game_screen.width / 1.75,
                                                volume_controls_height, slategray, lightgray, True)

        if volume_up_button:
            print("volume increased!")
            music_object.change_music_volume(10)
        if volume_down_button:
            print("volume decreased!")
            music_object.change_music_volume(-10)

        if music_object.volume_level == 0:
            create_onscreen_text(medium_font, thunderbird_red, "(muted)", game_screen.width / 2,
                                 volume_controls_height + 25, True)

        music_changer = create_text_button(intermediate_font, white, "Change Music Track", game_screen.width / 2,
                                           game_screen.height / 2, slategray, lightgray, True)

        if music_changer:
            print("Track change initiated")
            music_object.cycle_track()

        current_track_name = music_object.tracklist[music_object.current_track_index][6:-4]
        create_onscreen_text(sml_med_font, blackish, f"Current Track: {current_track_name}", game_screen.width / 2,
                             game_screen.height / 1.6, True)

        return_button = create_text_button(intermediate_font, white, "Return", game_screen.width / 2,
                                           game_screen.height / 1.25, slategray, lightgray, True)

        if return_button:
            if GameHandler.game_status == "pregame":
                main_menu()
            elif GameHandler.game_status == "ongoing":
                connect_game()

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(15)


def mode_selection():

    while True:
        game_screen.screen.fill((100, 200, 200))

        game_mode_list = [connect4, connect3, wide_boi, tall_boi, tic_tac_toe, cheese_crackers, deluxe, custom_mode]

        base_height = game_screen.height * 0.18
        height_multiplier = 1

        for index, mode in enumerate(game_mode_list, 1):
            button = create_text_button(sml_med_font, white, f"{index}. {mode.title}", game_screen.width / 4,
                                        base_height * height_multiplier, lighter_green, green, False)
            if button:
                GridManager.grid = []
                GameHandler.current_mode = mode
                coin_flip()

            height_multiplier += 0.5

        back_button = create_text_button(medium_font, black, "Back", game_screen.width * .8,
                                         game_screen.height * 0.02, (250, 0, 0), (180, 0, 0), True)
        if back_button:
            main_menu()

        music_button = create_text_button(small_font, blackish, "Toggle Music", game_screen.width * .925,
                                          game_screen.height * 0.035, lightgray, slategray, True)

        if music_button:
            music_object.music_toggle()

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(15)


def coin_flip():

    coin_flip_text = "Let's flip a coin to decide who goes first. Choose Heads or Tails:"

    flip_choice_made = False

    flip_frame_counter = 1

    player_call = None
    coin_flip_result = None

    coin_flip_frames = []
    while flip_frame_counter <= 14:
        coin_flip_frame_directory = f"images/coin-toss-frames/{flip_frame_counter}.png"
        coin_flip_frames.append(coin_flip_frame_directory)
        flip_frame_counter += 1

    current_frame_index = 0  # To follow the current state of the animation inside the loop
    number_of_iterations = 0  # Track the number of times that the animation has been completed

    while True:

        game_screen.screen.fill((90, 130, 50))

        create_onscreen_text(medium_font, white, coin_flip_text, game_screen.width/2, game_screen.height * 0.08, True)

        heads_button = create_text_button(intermediate_font, black, "HEADS", game_screen.width/7, game_screen.height *
                                          0.2, lighter_red if not flip_choice_made else slategray,
                                          red if not flip_choice_made else slategray, False, False)

        if heads_button:
            if not flip_choice_made:
                flip_choice_made = True
                player_call = "Heads"

        tails_button = create_text_button(intermediate_font, black, "TAILS", game_screen.width / 2.6, game_screen.height
                                          * 0.2, lighter_red if not flip_choice_made else slategray,
                                          red if not flip_choice_made else slategray, False, False)

        if tails_button:
            if not flip_choice_made:
                flip_choice_made = True
                player_call = "Tails"

        if heads_button or tails_button:
            coin_sound = mixer.Sound('audio/coin-flip.wav')
            mixer.Sound.play(coin_sound)
            coin_flip_result = random.choice(["Heads", "Tails"])

        if not flip_choice_made:
            game_screen.screen.blit(pygame.image.load(coin_flip_frames[0]), (game_screen.width / 9,
                                                                             game_screen.height / 3.2))

        if flip_choice_made:
            create_onscreen_text(medium_font, white, f"You have chosen {player_call}", game_screen.width * 0.62,
                                 game_screen.height * 0.35)
            game_screen.screen.blit(pygame.image.load(coin_flip_frames[current_frame_index]), (game_screen.width/9,
                                                                                               game_screen.height/3.2))
            current_frame_index += 1
            if current_frame_index >= len(coin_flip_frames) - 2:
                current_frame_index = 0
                number_of_iterations += 1
            result_text = "flipping..." if number_of_iterations < 3 else f"The result is... {coin_flip_result}!"
            create_onscreen_text(medium_font, white, result_text, game_screen.width * 0.62, game_screen.height / 2)
            win_loss_insert = "won" if player_call == coin_flip_result else "lost"
            GameHandler.priority = True if win_loss_insert == "won" else False
            win_loss_text = "" if number_of_iterations < 4 else f"You have {win_loss_insert} the coin toss!"
            create_onscreen_text(medium_font, white, win_loss_text, game_screen.width * 0.62, game_screen.height / 1.5)
            if number_of_iterations > 5:
                pre_game_rules(win_loss_insert)

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(8)


def pre_game_rules(flip_status):

    winner = "You have" if flip_status == "won" else "The opponent has"

    rules_choice_made = False
    display_rules = False
    # add a rules disabler

    pre_game_message = f"{winner} won the coin toss and will be going first!"

    game_rules = f" {GameHandler.current_mode.title} involves you and your opponent choosing to fill in slots on a " \
                 f"{GameHandler.current_mode.board.shape[0]} by {GameHandler.current_mode.board.shape[1]} board. " \
                 f"The goal of the game is to align {GameHandler.current_mode.objective} of your characters in a row " \
                 f"anywhere on the board before your opponent does. If the board fills up before either player " \
                 f"accomplishes this objective, the game ends in a tie."

    while True:
        game_screen.screen.fill((90, 110, 150))

        create_onscreen_text(sml_med_font, white, pre_game_message, game_screen.width / 2, game_screen.height / 17,
                             True)

        create_onscreen_text(sml_med_font, white, "Would you like to hear the rules?", game_screen.width / 2,
                             game_screen.height / 9, True)

        yes_button = create_text_button(intermediate_font, black, "YES", game_screen.width / 4, game_screen.height *
                                        0.2, lighter_red if not rules_choice_made else slategray,
                                        red if not rules_choice_made else slategray, False)

        if yes_button:
            if not rules_choice_made:
                rules_choice_made = True
                display_rules = True

        no_button = create_text_button(intermediate_font, black, "NO", game_screen.width / 1.5, game_screen.height
                                       * 0.2, lighter_red if not rules_choice_made else slategray,
                                       red if not rules_choice_made else slategray, False)

        if no_button:
            if not rules_choice_made:
                rules_choice_made = True

        if display_rules:
            display_text_over_multiple_lines(game_rules, sml_med_font, 50, game_screen.width / 4,
                                             game_screen.height * 0.4, 0.15)
        if not display_rules and rules_choice_made:
            create_onscreen_text(sml_med_font, black, "Fine, be that way...", game_screen.width / 4,
                                 game_screen.height * 0.4)

        proceed_button = create_text_button(large_font, black, "Proceed To The Game", game_screen.width/2,
                                            game_screen.height*0.8, (90, 90, 255), (90, 90, 180), True)

        if proceed_button:
            connect_game()

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(8)


def connect_game():

    GameHandler.game_status = "ongoing"

    GameHandler.player_turn = True if GameHandler.priority else False

    grid_manager.generate_grid()  # Creating the grid

    while True:

        game_screen.screen.fill(thistle_green)

        create_onscreen_text(intermediate_font, (0, 200, 0), "Player Turn", game_screen.width / 2,
                             game_screen.height * 0.01, True) if GameHandler.player_turn else \
            create_onscreen_text(intermediate_font, red, "CPU Turn", game_screen.width / 2, game_screen.height * 0.01,
                                 True)

        music_toggle = create_text_button(small_font, thunderbird_red, "Toggle Music", game_screen.width * .86,
                                          game_screen.height * 0.90, blackish, black, False)

        if music_toggle:
            music_object.music_toggle()

        options_button = create_text_button(sml_med_font, white, "Options Menu", game_screen.width * .85, 0,
                                            (0, 200, 0), green, False)

        if options_button:
            sound_menu()

        grid_manager.blit_grid()  # Displaying the grid, also contains the cells and their interactions

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()  # Updating the game display
        clock.tick(60)  # Frame-rate

        for symbol in [GameHandler.player_symbol, GameHandler.enemy_symbol]:
            win_loss_check(symbol)

        if not GameHandler.player_turn:
            if not GameHandler.time_taken:
                GameHandler.enemy_turn_start_time = pygame.time.get_ticks()
                GameHandler.time_taken = True
            enemy_turn()

        if GameHandler.game_status in ["won", "lost", "tied"]:
            post_game()


def post_game():

    header_message = f"You have {GameHandler.game_status} the game!"

    replay_saved = False

    win_sound = mixer.Sound("audio/win.wav")
    lose_sound = mixer.Sound("audio/lose.wav")
    tie_sound = mixer.Sound("audio/tie.mp3")

    if GameHandler.game_status == "won":
        mixer.Sound.play(win_sound)
    elif GameHandler.game_status == "lost":
        mixer.Sound.play(lose_sound)
    elif GameHandler.game_status == "tied":
        mixer.Sound.play(tie_sound)

    while True:

        game_screen.screen.fill((55, 195, 120))

        create_onscreen_text(large_font, black, header_message, game_screen.width / 2, game_screen.height * 0.05, True)

        replay_button = create_text_button(intermediate_font, black if not replay_saved else white,
                                           "Save Replay?" if not replay_saved else "Saved",
                                           game_screen.width / 2, game_screen.height * 0.4,
                                           slategray if not replay_saved else black,
                                           lightgray if not replay_saved else black, True)
        if replay_button and not replay_saved:
            for replay in ReplayManager.replay_list:
                if replay.name == "Empty":
                    print("Filling empty replay slot...")
                    replay.name = "Filled"
                    replay.game_mode = GameHandler.current_mode
                    replay.player_moves = DataTracker.player_move_list
                    replay.enemy_moves = DataTracker.enemy_move_list
                    replay.priority = GameHandler.priority
                    replay.player_symbol = GameHandler.player_symbol
                    replay.enemy_symbol = GameHandler.enemy_symbol
                    print("Replay saved!")
                    replay_saved = True
                    break

            create_onscreen_text(medium_font, black, "Done", game_screen.width / 2, game_screen.height * 0.65, True)

        return_button = create_text_button(medium_font, black, "main menu", game_screen.width / 2,
                                           game_screen.height * 0.8, slategray, lightgray, True)

        if return_button:
            post_game_reset()
            main_menu()

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(15)
# ----------------------------------------------------------------------------------------------------------------------
# Connect X Gameplay Logic


class GridCell:  # Currently generated inside the GridManager.generate_and_blit_grid() method
    def __init__(self, cid: tuple[int, int], pos_factors: tuple[float, float]):
        self.cid = cid
        self.value = ""
        self.position_factors = pos_factors  # The game-mode-dependent offsets that cells are generated with
        self.width = GameHandler.current_mode.cell_width
        self.height = GameHandler.current_mode.cell_height
        self.x = None
        self.y = None

        self.is_victory_cell = False  # To single out a few to be highlighted when a game is won
        self.is_hovered = False

    def generate_cell_on_board(self):

        mouse = pygame.mouse.get_pos()

        x = game_screen.width * self.position_factors[0]
        y = game_screen.height * self.position_factors[1]
        self.x, self.y = x, y

        outline_rect = pygame.Rect(x, y, self.width, self.height)

        if x + self.width > mouse[0] > x and y + self.height > mouse[1] > y and GameHandler.player_turn == True:
            pygame.draw.rect(game_screen.screen, white, outline_rect, int(game_screen.height / 360))
            if not self.is_hovered:
                hover_sound = mixer.Sound('audio/button_click.mp3')
                mixer.Sound.play(hover_sound)
                self.is_hovered = True
            for evnt in pygame.event.get():
                if evnt.type == pygame.MOUSEBUTTONUP:  # Detecting clicks
                    return x, y, self.width, self.height
        elif x + self.width > mouse[0] > x and y + self.height > mouse[1] > y and GameHandler.player_turn == False:
            pygame.draw.rect(game_screen.screen, red, outline_rect, int(game_screen.height / 360))
            if not self.is_hovered:
                hover_sound = mixer.Sound('audio/button_click.mp3')
                mixer.Sound.play(hover_sound)
                self.is_hovered = True
            for evnt in pygame.event.get():
                if evnt.type == pygame.MOUSEBUTTONUP:  # Detecting clicks
                    rejection_sound = mixer.Sound('audio/rejection.wav')
                    mixer.Sound.play(rejection_sound)
        else:  # Non-hover
            self.is_hovered = False
            pygame.draw.rect(game_screen.screen, black, outline_rect, int(game_screen.height / 360))

    def draw_cell_value(self):
        create_onscreen_text(GameHandler.current_mode.font, black, self.value, self.x + (self.width / 3),
                             self.y + (self.height / 6))


class GridManager:

    def __init__(self, grid: list[list[GridCell]]):
        self.grid = grid

    def generate_grid(self):
        grid: list[list] = []
        y_offset_factor = GameHandler.current_mode.cell_y_offset  # Vertical Spacing
        for row in range(GameHandler.current_mode.board.shape[0]):

            x_offset_factor = GameHandler.current_mode.cell_x_offset  # Horizontal spacing
            grid_row: list = []  # The rows of the overall grid that will be inserted

            for col in range(GameHandler.current_mode.board.shape[1]):

                cell = GridCell((row, col), (x_offset_factor, y_offset_factor))
                grid_row.append(cell)
                x_offset_factor += GameHandler.current_mode.x_offset_step

            grid.append(grid_row)
            y_offset_factor += GameHandler.current_mode.y_offset_step

        if not self.grid:
            print("GameHandler grid is currently empty. Populating...")
            self.grid = grid

    def generate_replay_grid(self, replay):
        grid: list[list[GridCell]] = []
        y_offset_factor = replay.game_mode.cell_y_offset
        for row in range(replay.game_mode.board.shape[0]):

            x_offset_factor = replay.game_mode.cell_x_offset
            grid_row: list[GridCell] = []

            for col in range(replay.game_mode.board.shape[1]):

                cell = GridCell((row, col), (x_offset_factor, y_offset_factor))
                grid_row.append(cell)
                x_offset_factor += replay.game_mode.x_offset_step

            grid.append(grid_row)
            y_offset_factor += replay.game_mode.y_offset_step

        if not self.grid:
            print("Generating replay grid...")
            self.grid = grid

    def blit_grid(self):
        if not self.grid:
            print("The game grid does not exist, something went wrong. Resetting.")
            main()
        for row in self.grid:
            for cell in row:
                physical_cell = cell.generate_cell_on_board()
                if cell.value:
                    cell.draw_cell_value()
                if physical_cell and GameHandler.player_turn and GameHandler.game_status == "ongoing":
                    print(f"The player has claimed a cell! ({cell.cid})")
                    stamp_sound = mixer.Sound("audio/kermite607_stamp.wav")
                    mixer.Sound.play(stamp_sound)
                    cell.value = GameHandler.player_symbol
                    DataTracker.player_move_list.append(cell.cid)
                    GameHandler.player_turn = False


grid_manager = GridManager([])


def enemy_turn():

    goal_num: int = GameHandler.current_mode.objective  # Number of aligned squares in order to win

    winning_moves: list = []  # Moves that can win the CPU the game
    defensive_moves: list = []  # Moves that can stop the player from winning
    optimal_moves: list = []  # Moves that can build towards a win

    current_time = pygame.time.get_ticks()
    if current_time - GameHandler.enemy_turn_start_time >= GameHandler.enemy_turn_length \
            and GameHandler.game_status == "ongoing":

        for symbol in [GameHandler.enemy_symbol, GameHandler.player_symbol]:

            # Method 1: Checking rows
            for r_ind, row in enumerate(grid_manager.grid):

                symbol_count = 0
                for c_ind, cell in enumerate(row):
                    if cell.value == symbol:
                        symbol_count += 1
                    else:  # Reset the count
                        symbol_count = 0
                    if symbol_count == goal_num - 1:  # If symbol count is one short of the goal

                        fail_roll = random.randint(1, 100)  # Chance for CPU to do nothing
                        if fail_roll < GameHandler.difficulty:  # CPU does act

                            # CPU will try to find the 2 potential cells that can complete the row

                            # The far (rightmost) space
                            try:
                                if not grid_manager.grid[r_ind][c_ind + 1].value:  # Cell exists and is valueless
                                    if symbol == GameHandler.player_symbol:
                                        print("Defensive move found")
                                        defensive_moves.append(grid_manager.grid[r_ind][c_ind + 1])
                                    elif symbol == GameHandler.enemy_symbol:
                                        print("Winning move found")
                                        winning_moves.append(grid_manager.grid[r_ind][c_ind + 1])
                            except IndexError:
                                pass  # If space does not exist, ignore

                            # The near (leftmost) space
                            try:
                                if not grid_manager.grid[r_ind][c_ind - (goal_num - 1)].value and \
                                        c_ind - (goal_num - 1) >= 0:
                                    if symbol == GameHandler.player_symbol:
                                        print("Defensive move found")
                                        defensive_moves.append(grid_manager.grid[r_ind][c_ind - (goal_num - 1)])
                                    elif symbol == GameHandler.enemy_symbol:
                                        print("Winning move found")
                                        winning_moves.append(grid_manager.grid[r_ind][c_ind - (goal_num - 1)])
                            except IndexError:
                                pass  # If space does not exist, ignore

        # Collecting existing moves from lists and executing one

        def resolve_enemy_turn(chosen_cell):
            chosen_cell.value = GameHandler.enemy_symbol
            DataTracker.enemy_move_list.append(chosen_cell.cid)
            print(f"The enemy has successfully selected cell {chosen_cell.cid}!")
            GameHandler.player_turn = True
            GameHandler.time_taken = False

        def move_decision(list_of_cell_lists: list[list[GridCell]]):
            for option_list in list_of_cell_lists:
                if len(option_list) >= 1:
                    for g_cell in option_list:
                        print(g_cell.cid)
                    cell_chosen = random.choice(option_list)
                    resolve_enemy_turn(cell_chosen)
                    return True
            return False

        move_made: bool = move_decision([winning_moves, defensive_moves, optimal_moves])

        if move_made:
            print("Move was made")
            return

        # Final method: Random selection
        if not move_made:
            row_choice = random.choice(grid_manager.grid)
            cell_choice = random.choice(row_choice)

            print(cell_choice.cid)

            if not cell_choice.value:

                stamp_sound = mixer.Sound("audio/kermite607_stamp.wav")
                mixer.Sound.play(stamp_sound)

                resolve_enemy_turn(cell_choice)
                return
            else:
                enemy_turn()  # Recurse


def tie_check():
    open_cells: int = 0
    for row in grid_manager.grid:
        for cell in row:
            if not cell.value:
                open_cells += 1
    if open_cells == 0 and GameHandler == "ongoing":
        print("There are no more available squares and no one has won. The game ends in a tie!")
        GameHandler.game_status = "tied"
        return


def win_loss_check(symbol):

    # Checking rows (horizontal)
    for row in grid_manager.grid:
        symbol_count = 0
        for cell in row:
            if cell.value == symbol:
                symbol_count += 1
            else:  # Reset the count
                symbol_count = 0
            if symbol_count == GameHandler.current_mode.objective:
                print("Victory condition reached (row)")
                if symbol == GameHandler.player_symbol:
                    GameHandler.game_status = "won"
                    return
                if symbol == GameHandler.enemy_symbol:
                    GameHandler.game_status = "lost"
                    return

    # Checking columns
    column_count = 0
    while column_count <= GameHandler.current_mode.board.shape[1] - 1:
        symbol_count = 0
        for row in grid_manager.grid:
            if row[column_count].value == symbol:
                symbol_count += 1
            else:
                symbol_count = 0
            if symbol_count == GameHandler.current_mode.objective:
                print("Victory condition reached (column)")
                if symbol == GameHandler.player_symbol:
                    GameHandler.game_status = "won"
                    return
                if symbol == GameHandler.enemy_symbol:
                    GameHandler.game_status = "lost"
                    return

        column_count += 1

    # Checking forward-diagonals
    for row_ind, row in enumerate(grid_manager.grid):
        for col_ind, cell in enumerate(row):
            y = row_ind
            x = col_ind

            symbol_count = 0

            board_size_y = GameHandler.current_mode.board.shape[0]
            board_size_x = GameHandler.current_mode.board.shape[1]

            while True:
                if y > board_size_y - 1 or x > board_size_x - 1:  # If values were larger than grid can support
                    break

                else:
                    if grid_manager.grid[y][x].value == symbol:
                        y += 1
                        x += 1
                        symbol_count += 1
                        if symbol_count == GameHandler.current_mode.objective:
                            print("Victory condition reached (forward diagonal)")
                            if symbol == GameHandler.player_symbol:
                                GameHandler.game_status = "won"
                                return
                            if symbol == GameHandler.enemy_symbol:
                                GameHandler.game_status = "lost"
                                return
                    else:
                        break

    # Checking backwards diagonals
    for row_ind, row in enumerate(grid_manager.grid):
        for col_ind, cell in enumerate(row):
            y = row_ind
            x = col_ind

            symbol_count = 0

            board_size_y = GameHandler.current_mode.board.shape[0]

            while True:

                if y > board_size_y - 1 or x < 0:
                    break

                else:
                    if grid_manager.grid[y][x].value == symbol:
                        y += 1
                        x -= 1
                        symbol_count += 1
                        if symbol_count == GameHandler.current_mode.objective:
                            print("Victory condition reached (backward diagonal)")
                            if symbol == GameHandler.player_symbol:
                                GameHandler.game_status = "won"
                                return
                            if symbol == GameHandler.enemy_symbol:
                                GameHandler.game_status = "lost"
                                return

                    else:
                        break

    tie_check()


def post_game_reset():

    if GameHandler.game_status == "won":
        DataTracker.wins.value += 1
    elif GameHandler.game_status == "lost":
        DataTracker.losses.value += 1
    elif GameHandler.game_status == "tied":
        DataTracker.ties.value += 1

    grid_manager.grid = []
    DataTracker.player_move_list = []
    DataTracker.enemy_move_list = []
    GameHandler.game_status = "pregame"
    GameHandler.player_turn = None

# ----------------------------------------------------------------------------------------------------------------------


def main():

    while True:

        title_screen()

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(15)


if __name__ == "__main__":
    print("------------------------------------------------------------------------------")
    main()
