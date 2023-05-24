import sys
import pygame
from pygame import mixer
import random
import math
from dataclasses import dataclass
import numpy as np
import shelve
# import string
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
                return Replay(obj.id, "Replay", tic_tac_toe, [], [], True, (), 0)

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

# Setting different sized font options to be used later for general text and button labels
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


def create_onscreen_text(font_size, color, message, x, y,):

    text = font_size.render(message, True, color)

    game_screen.screen.blit(text, (x, y))


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


def create_text_button(font_choice, text_color, msg, x, y, hover_color, default_color, x_adjust: bool):

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
                return True
    else:
        pygame.draw.rect(game_screen.screen, default_color, (x, y, button_width, button_height))

    game_screen.screen.blit(button_msg, (x + button_width / 10, y + button_height / 10))


# ----------------------------------------------------------------------------------------------------------------------
# 3. Defining the GameMode class and creating several instances representing a variety of playable game modes


@dataclass()
class GameMode:
    title: str  # The name of the game mode
    board: np.ndarray  # The arrangement/dimensions of the game board
    objective: int  # The number of consecutive characters needed to win


connect4 = GameMode("Connect4", np.full((6, 7), "-"), 4)

connect3 = GameMode("Connect3", np.full((4, 5), "-"), 3)

wide_boi = GameMode("Wide Boi", np.full((4, 8), "-"), 4)

tall_boi = GameMode("Tall Boi", np.full((8, 4), "-"), 4)

tic_tac_toe = GameMode("Tic-Tac-Toe", np.full((3, 3), "-"), 3)

cheese_crackers = GameMode("Cheese & Crackers", np.full((5, 5), "-"), 4)

deluxe = GameMode("Connect6", np.full((9, 10), "-"), 6)

custom_mode = GameMode("Custom", np.full((99, 99), "-"), 99)  # Not meant to be played in this form


# ----------------------------------------------------------------------------------------------------------------------
# 4. DEFINING THE STAT CLASS AND THE REPLAY CLASS TO TRACK IN-GAME HISTORY


@dataclass()
class Stat:
    name: str  # The name of the stat in question
    value: int  # the value of that statistic


wins = Stat("Wins", 0)
losses = Stat("Losses", 0)
ties = Stat("Ties", 0)


@dataclass()
class Replay:
    id: str  # Unchanging unique identifier for each replay instance
    name: str  # Name of the replay, can be edited by the user
    game_mode: GameMode  # In which game mode did the game take place
    player_moves: list  # The sequence of moves that the player made
    enemy_moves: list  # The sequence of moves that the enemy made
    priority: bool  # Whether player had the priority in the game or not
    symbols: tuple  # The symbols used in the game (player symbol, enemy symbol)
    turn_count: int  # The number of turns the game took

    def __str__(self):
        return f"Replay: {self.name}, Mode: {self.game_mode.title}, Turns: {self.turn_count}"


class ReplayManager:
    r1 = Replay("r1", "Replay", tic_tac_toe, [], [], True, (), 0)
    r2 = Replay("r2", "Replay", tic_tac_toe, [], [], True, (), 0)
    r3 = Replay("r3", "Replay", tic_tac_toe, [], [], True, (), 0)
    r4 = Replay("r4", "Replay", tic_tac_toe, [], [], True, (), 0)
    r5 = Replay("r5", "Replay", tic_tac_toe, [], [], True, (), 0)


# ----------------------------------------------------------------------------------------------------------------------
# 5. DEFINING GLOBAL VARIABLES


class GameHandler:
    current_mode = connect4
    board = current_mode.board  # The board of the active game format
    player_symbol: str = var_save_value(save_file, "player_symbol", "X")
    enemy_symbol: str = var_save_value(save_file, "enemy_symbol", "O")
    session_counter: int = 0
    priority: bool = True
    player_turn = True
    enemy_turn_length = 5000  # in milliseconds
    enemy_turn_start_time = 1  # Will contain the pygame.time.getticks() of when the CPU's turn began
    time_taken = False  # Bool to show that the enemy_turn_start_time was taken


active_game = connect4  # The active game format in use

objective = active_game.objective  # The objective of the active game format

# Determines whether the game is active and certain functions should continue
game_is_active: bool = True

# Variable controlling whether to ask if the rules should be explained
rule_toggle: bool = True

session_counter = 0

# Sets of acceptable positive and negative responses to input prompts
positive_response_list: list = ["Yes", "Y", "Yup", "Affirmative", "Yeah", "Yeayuh", "10-4", "Oui", "Confirm"]
negative_response_list: list = ["No", "Nay", "Negative", "N", "Nope", "Nuh-uh", "Niet", "Non", "Nah", "Deny"]

# Setting a difficulty level variable
difficulty: int = 80

player_move_list: list = []  # A list that will contain the sequence of all the moves the player makes

enemy_move_list: list = []  # A list that will contain the sequence of all the moves the CPU makes

# ----------------------------------------------------------------------------------------------------------------------
# 6. Initializing all shelved save data that the game tracks between sessions

print("Initializing save data... ")

wins.value = obtain_save_value(save_file, wins)
losses.value = obtain_save_value(save_file, losses)
ties.value = obtain_save_value(save_file, ties)

ReplayManager.r1 = obtain_save_value(save_file, ReplayManager.r1)
ReplayManager.r2 = obtain_save_value(save_file, ReplayManager.r2)
ReplayManager.r3 = obtain_save_value(save_file, ReplayManager.r3)
ReplayManager.r4 = obtain_save_value(save_file, ReplayManager.r4)
ReplayManager.r5 = obtain_save_value(save_file, ReplayManager.r5)

# Initialize list after save data is potentially retrieved
replay_list: list = [ReplayManager.r1, ReplayManager.r2, ReplayManager.r3, ReplayManager.r4, ReplayManager.r5]

# Initialize the user-made custom mode, if it exists in the save file
custom_mode = obtain_save_value(save_file, custom_mode)

# When game mode win counters start being tracked, their "shelve" name will be obj.name.strip() (to remove spaces)

# ----------------------------------------------------------------------------------------------------------------------
# 8. Menu, game mode selection (and creation), and board display functions


def title_screen():

    start_text = intermediate_font.render("Connect X", True, white)
    credit_text = sml_med_font.render("by Benndot", True, white)

    title_image = pygame.image.load("images/connect4-board-pic.jpg")

    nav_bar_height = game_screen.height / 7

    # Scales the start screen image to the screen size
    title_image = pygame.transform.scale(title_image, (game_screen.width, game_screen.height - (game_screen.height / 10)
                                                       ))

    while True:
        game_screen.screen.fill((0, 0, 200))
        game_screen.screen.blit(start_text, ((game_screen.width - start_text.get_width()) / 2, game_screen.height / 75))
        game_screen.screen.blit(credit_text, ((game_screen.width - start_text.get_width()) / 1.9,
                                              game_screen.height / 12))

        start_button = create_text_button(medium_font, black, "Start", game_screen.width * .15, game_screen.height *
                                          0.02, green, lighter_green, True)

        if start_button:
            main_menu()

        options_button = create_text_button(medium_font, black, "Options", game_screen.width * .8,
                                            game_screen.height * 0.02, (200, 200, 0), (120, 120, 0), True)

        if options_button:
            options_menu()

        music_button = create_text_button(small_font, blackish, "Toggle Music", game_screen.width * .925,
                                          game_screen.height * 0.035, lightgray, slategray, True)

        if music_button:
            music_object.music_toggle()

        ghost_button = create_transparent_button(250, 100, game_screen.width / 1.75, game_screen.height / 2.8)

        if ghost_button:
            print("ghost")

        game_screen.screen.blit(title_image, (0, nav_bar_height))

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(15)


def main_menu():

    greeting_message = "Welcome to Benndot's Connect X game!" if GameHandler.session_counter == 0 else \
        "Welcome back to Benndot's Connect X game!"

    play_game_str = {"Play GameHandler": mode_selection}
    change_symbol_str = {"Change Symbol": mode_selection}
    stats_replays_str = {"Stats and Replays": mode_selection}
    audio_options = {"Audio Options": options_menu}
    save_options_str = {"Save File Options": options_menu}
    quit_game_str = {"Quit GameHandler": sys.exit}

    menu_options = [play_game_str, change_symbol_str, stats_replays_str, audio_options, save_options_str, quit_game_str]

    while True:

        game_screen.screen.fill((230, 60, 160))

        create_onscreen_text(medium_font, black, greeting_message, game_screen.width / 4, game_screen.height * 0.05)

        base_height = game_screen.height * 0.25
        height_multiplier = 1
        for index, option in enumerate(menu_options):
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


def mode_selection():
    # Initialize list here, so deleted custom mode values can be updated, and since nowhere else uses this anyway

    while True:
        game_screen.screen.fill((100, 200, 200))

        game_mode_list = [connect4, connect3, wide_boi, tall_boi, tic_tac_toe, cheese_crackers, deluxe, custom_mode]

        base_height = game_screen.height * 0.18
        height_multiplier = 1
        for index, mode in enumerate(game_mode_list):
            button = create_text_button(sml_med_font, white, f"{index}. {mode.title}", game_screen.width / 4,
                                        base_height * height_multiplier, lighter_green, green, False)
            if button:
                coin_flip()

            height_multiplier += 0.5

        back_button = create_text_button(medium_font, black, "Back", game_screen.width * .8,
                                         game_screen.height * 0.02, (250, 0, 0), (180, 0, 0), True)
        if back_button:
            main()

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

        create_onscreen_text(medium_font, white, coin_flip_text, game_screen.width/20, game_screen.height * 0.08)

        heads_button = create_text_button(intermediate_font, black, "HEADS", game_screen.width/7, game_screen.height *
                                          0.2, lighter_red if not flip_choice_made else slategray,
                                          red if not flip_choice_made else slategray, False)

        if heads_button:
            if not flip_choice_made:
                flip_choice_made = True
                player_call = "Heads"

        tails_button = create_text_button(intermediate_font, black, "TAILS", game_screen.width / 2.6, game_screen.height
                                          * 0.2, lighter_red if not flip_choice_made else slategray,
                                          red if not flip_choice_made else slategray, False)

        if tails_button:
            if not flip_choice_made:
                flip_choice_made = True
                player_call = "Tails"

        if heads_button or tails_button:
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

    game_rules = f"{GameHandler.current_mode.title} involves you and your opponent choosing to fill in slots on a " \
                 f"{GameHandler.current_mode.board.shape[0]} by {GameHandler.current_mode.board.shape[1]} board. " \
                 f"The goal of the game is to align {GameHandler.current_mode.objective} of your characters in a row " \
                 f"anywhere on the board before your opponent does. If the board fills up before either player " \
                 f"accomplishes this objective, the game ends in a tie."

    while True:
        game_screen.screen.fill((90, 110, 150))

        create_onscreen_text(sml_med_font, white, pre_game_message, game_screen.width / 5, game_screen.height / 17)

        create_onscreen_text(sml_med_font, white, "Would you like to hear the rules?", game_screen.width / 5,
                             game_screen.height / 9)

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
            entry_x = game_screen.width / 4
            start_index = 0
            height_offset = 1
            index_counter = 0
            for index, char in enumerate(game_rules):
                index_counter += 1
                if char == " " and index_counter >= 50:
                    end_index = index + 1
                    create_onscreen_text(sml_med_font, black, game_rules[start_index: end_index],
                                         entry_x,
                                         game_screen.height * 0.4 * height_offset)
                    height_offset += 0.15
                    start_index = index
                    index_counter = 0
                if index >= len(game_rules) - 1:
                    create_onscreen_text(sml_med_font, black, game_rules[start_index: -1],
                                         entry_x, game_screen.height * 0.4 * height_offset)
                    break

        proceed_button = create_text_button(large_font, black, "Proceed To The GameHandler", game_screen.width/2,
                                            game_screen.height*0.8, (0, 0, 255), (0, 0, 180), True)

        if proceed_button:
            connect_game()

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(8)


def options_menu():

    title_text = large_font.render("Options Menu", True, blackish)

    while True:
        game_screen.screen.fill(thistle_green)
        game_screen.screen.blit(title_text, ((game_screen.width - title_text.get_width()) / 2, 0))

        music_button = create_text_button(medium_font, white, "Toggle Music", game_screen.width / 1.97,
                                          game_screen.height / 6.5, lightgray, slategray, True)
        if music_button:
            music_object.music_toggle()

        # Bool declaration
        music_pause_declaration = "Yes" if music_object.music_paused else "No"
        music_paused_text = medium_font.render(f"Music Paused: " + music_pause_declaration, True, blackish)
        bool_text_x = (game_screen.width - music_paused_text.get_width()) / 2
        bool_text_y = (game_screen.height - music_paused_text.get_height()) / 3.8
        game_screen.screen.blit(music_paused_text, (bool_text_x, bool_text_y))

        volume_height = game_screen.height / 2.8
        volume_text = medium_font.render(f"{music_object.volume_level}", True, black)
        volume_text_x = (game_screen.width / 2) - (volume_text.get_width() / 2) + 5
        game_screen.screen.blit(volume_text, (volume_text_x, volume_height - 10))

        volume_up_button = create_text_button(small_font, white, "Volume +", game_screen.width / 2.25,
                                              volume_height, slategray, lightgray, True)

        volume_down_button = create_text_button(small_font, white, "Volume -", game_screen.width / 1.75,
                                                volume_height, slategray, lightgray, True)

        if volume_up_button:
            print("volume increased!")
            music_object.change_music_volume(10)
        if volume_down_button:
            print("volume decreased!")
            music_object.change_music_volume(-10)

        if music_object.volume_level == 0:
            muted_text = medium_font.render("(muted)", True, thunderbird_red)
            game_screen.screen.blit(muted_text, (volume_text_x * .92, volume_height + 25))

        music_changer = create_text_button(intermediate_font, white, "Change Music Track", game_screen.width / 2,
                                           game_screen.height / 2.2, slategray, lightgray, True)

        if music_changer:
            print("Track change initiated")
            music_object.cycle_track()

        current_track_name = music_object.tracklist[music_object.current_track_index][6:-4] if \
            music_object.current_track_index != 13 else "    ????????????????????"
        current_track_text = sml_med_font.render(f'Current Track: ' + current_track_name, True, blackish)
        game_screen.screen.blit(current_track_text, (game_screen.width / 6, game_screen.height / 1.6))

        # Return to start menu button
        return_button = create_text_button(medium_font, white, "Return To Start", game_screen.width / 2,
                                           game_screen.height / 1.25, slategray, lightgray, True)

        if return_button:
            title_screen()

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(15)


def connect_game():

    GameHandler.player_turn = True if GameHandler.priority else False

    grid_manager.generate_grid()  # Creating the grid

    while True:

        game_screen.screen.fill(thistle_green)

        create_onscreen_text(intermediate_font, black, "Player Turn" if GameHandler.player_turn else "CPU Turn",
                             game_screen.width / 2.5, game_screen.height * 0.01)

        music_toggle = create_text_button(small_font, thunderbird_red, "Toggle Music", game_screen.width * .86,
                                          game_screen.height * 0.90, blackish, black, False)

        if music_toggle:
            music_object.music_toggle()

        options_button = create_text_button(sml_med_font, white, "Options Menu", game_screen.width * .85, 0,
                                            (0, 200, 0), green, False)

        if options_button:
            options_menu()

        grid_manager.blit_grid()  # Displaying the grid

        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evnt.type == pygame.MOUSEBUTTONDOWN:
                pass

            if evnt.type == pygame.KEYDOWN:
                pass

        pygame.display.update()
        clock.tick(60)  # Frame-rate

        if not GameHandler.player_turn:
            if not GameHandler.time_taken:
                GameHandler.enemy_turn_start_time = pygame.time.get_ticks()
                GameHandler.time_taken = True
            enemy_turn()


# ----------------------------------------------------------------------------------------------------------------------
# Connect X Gameplay Logic

class GridCell:  # Currently generated inside the GridManager.generate_and_blit_grid() method
    def __init__(self, cell_id: tuple[int, int], pos_factors: tuple[float, float]):
        self.cell_id = cell_id
        self.position_factors = pos_factors
        self.value = ""
        self.width = game_screen.width / 10
        self.height = game_screen.height / 7
        self.x = None
        self.y = None

    def generate_cell_on_board(self):

        mouse = pygame.mouse.get_pos()

        x = game_screen.width * self.position_factors[0]
        y = game_screen.height * self.position_factors[1]
        self.x, self.y = x, y

        outline_rect = pygame.Rect(x, y, self.width, self.height)

        if x + self.width > mouse[0] > x and y + self.height > mouse[1] > y:  # Hover
            pygame.draw.rect(game_screen.screen, white, outline_rect, int(game_screen.height / 360))
            for evnt in pygame.event.get():
                if evnt.type == pygame.MOUSEBUTTONUP:  # Detecting clicks
                    return x, y, self.width, self.height
        else:  # Non-hover
            pygame.draw.rect(game_screen.screen, black, outline_rect, int(game_screen.height / 360))

    def draw_cell_value(self):
        create_onscreen_text(large_font, black, GameHandler.player_symbol, self.x + (self.width / 3),
                             self.y + (self.height / 6))


class GridManager:

    def __init__(self, grid: list[list[GridCell]], filled_cells: list):
        self.grid = grid
        self.filled_cells = filled_cells  # Cells with a value

    def generate_grid(self):
        grid: list[list] = []
        y_offset_factor = 0.1  # Vertical Spacing
        for row in range(GameHandler.current_mode.board.shape[0]):

            x_offset_factor = 0.15  # Horizontal spacing
            grid_row: list = []  # The rows of the overall grid that will be inserted

            for col in range(GameHandler.current_mode.board.shape[1]):

                cell = GridCell((row, col), (x_offset_factor, y_offset_factor))
                grid_row.append(cell)
                x_offset_factor += 0.1

            grid.append(grid_row)
            y_offset_factor += 0.15

        if not self.grid:
            print("GameHandler grid is currently empty. Populating...")
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
                if physical_cell and GameHandler.player_turn:
                    print("A cell has been claimed!")
                    cell.value = GameHandler.player_symbol
                    GameHandler.player_turn = False


grid_manager = GridManager([], [])


def enemy_turn():
    current_time = pygame.time.get_ticks()
    if current_time - GameHandler.enemy_turn_start_time >= GameHandler.enemy_turn_length:

        for row in grid_manager.grid:
            pass
            for cell in row:
                if cell.value:
                    pass
        print("Conditions were met!")
        GameHandler.player_turn = True
        GameHandler.time_taken = False
        return
    # Should have a little time delay before switching over


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
