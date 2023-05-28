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
is filled with the user's symbol. The CPU for their part, randomly selects their own square during their turn. Win and 
tie checks are then run to determine if either player has won. 

If the win / tie check comes up positive, the user is brought to a post-game screen where the user will eventually 
be able to save replays, resets are conducted on the game logic, and the user can return to the main menu to play again.

---

In terms of working side features so far, there is the music menu and symbol selection. 

The music menu controls the game's soundtrack, which acts as the backing music for the entire game. From here, the user
can choose to mute the music, change which track is playing, or tweak the music's volume. Mute buttons, however, are
to be found all over the game is various spots, for the sake of convenience. 

The symbol selection screen allows the user to choose which character (letter, number, punctuation) will represent them
and their opponent in-game. To input boxes exist for this purpose and for the changes to go through, they must be 
confirmed with a button press. 
 
### TODO

Create replay playback and replay deleting feature

implement basic save file features

More advanced enemy AI features

Create a short pause between win/loss/tie move and the user being brought the post-game screen

Create more viable game modes by properly sizing cells based on the amount of space available

confirmation / warning messages for symbol selection confirmation button presses

