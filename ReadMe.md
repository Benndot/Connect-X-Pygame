# Connect X - Pygame

## Introduction

This is my attempt to create a visual "Connect X" (Think Connect 4, TicTacToe, etc) using the Pygame library. 

The logic and structure of my game is largely based on an earlier project I made that was text-based and existed
entirely in the command terminal environment. 

This project demonstrates some new concepts for me, such as (simple) animations present in some screens, and well as 
working with more complex gameplay systems under the Pygame library than I have previously. 

## Current Content and Structure

The app's core functionality is current up and running. The connect X games are playable, and the game loop 
(gameplay, outcome checks, post-game resets, navigation) is functional. Some game modes have not yet been sized 
properly to the display, so they may not be playable. 

The game's structure is relatively simple. The game launches into a title screen. It then proceeds into a main menu
that offers submenus, and opportunity to start a game. 

Choosing to play will allow the user to pick a game mode from among a list given. Once chosen, the player is taken to
a new screen, where they are prompted to choose heads or tails. A coin flip sequence then follows to determine who gets
to go first. Finally, a pre-game screen offers the user the opportunity to review the game's rules before proceeding to
the game.

The game itself is your standard Tic-Tac-Toe / Connect X game. A grid is constructed, consisting of squares aligned in
rows and columns. Squares change color when hovered over, white if it's the player's turn and red if it isn't, and all 
actions on this grid have sound effects associated with them as well. Upon the user's click during their turn, a square 
is filled with the user's symbol. The CPU on their turn, has a variety of methods it uses to determine what move to
make. Win and tie checks are then run to determine if either player has won. 

If the win / tie check comes up positive, the user is brought to a post-game screen where the user can choose to save 
a replay of their game, which they can replay in the replay menu accessible from the main menu. Resets are afterward
conducted on the game logic, and the user can return to the main menu to play again indefinitely.

---

In terms of side features, there is currently the soundtrack / music menu, the symbol selection menu and the replay
menu / player. 

The music menu controls the game's soundtrack, which acts as the backing music for the entire game. From here, the user
can choose to mute the music, change which track is playing, or tweak the music's volume. Mute buttons, however, are
to be found all over the game is various spots, for the sake of convenience. 

The symbol selection screen allows the user to choose which character (letter, number, punctuation) will represent them
and their opponent in-game. To input boxes exist for this purpose and for the changes to go through, they must be 
confirmed with a button press. 

The replay menu allows the user to review and delete replays of previous games that they played and chose to save. 
Clicking on a replay takes them to the replay player, which allows them to cycle through the turns of the replay in
question. Each progress button click proceeds through a turn, showing both moves made in proper sequence. The replay 
can be reset to the beginning at any point. 

---

## CPU Logic 

The CPU logic works on 5 tiers of potential moves:

1. Winning: A move that will win it the game
2. Defensive: A move that will block a potential winning move of the player's 
3. Optimal: A move that will build on a chain of squares 2 or longer, but not long enough to win
4. Constructive: Moves that build towards winning, but not as much as optimal moves
5. Random: Decided through random selection

Each tier has priority after the next. 

An optimal move describes a move that won't win the CPU the game, but will build on two or more squares in a row in 
order to work towards that goal. 

A constructive move is one where either the CPU builds on a single one of their own squares to start a chain, or 
decides to claim a square inside two bounds of what could become a chain for the player. 
 
### TODO

implement basic save file (shelve) features

Create a short pause between win/loss/tie move and the user being brought the post-game screen, pause for enemy going
first on their first turn.

### Ideas

incorporate font sizes into game-mode adjustment options

custom game mode creation

make window resizable

highlight winning cells

confirmation / warning messages for symbol selection confirmation button presses

make grids dynamically-sized

