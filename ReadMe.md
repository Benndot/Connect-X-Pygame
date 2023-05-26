# Connect X - Pygame

This is my attempt to create a visual "Connect X" (Think Connect 4, TicTacToe, etc) using the Pygame library. 

The logic and structure of my game is going to be based on an earlier project I made that was text-based and existed
entirely in the command terminal environment. 

This project demonstrates some new concepts for me, such as (simple) animations present in some screens, and well as 
working with more complex gameplay systems under the Pygame library than I have previously. 

## Current State

The app currently has a basic version of everything leading up to the game itself working. Title screen, main menu,
pre-game rock-paper-scissors to determine who goes first. A pre-game rules screen as well. The main menu is mostly 
functional, but the symbol selection and replay menus it points to are just placeholders with no functionality. 

The rock-paper-scissors game is complete, and has some fun animated visuals and text. 

A multiple song soundtrack with an options menu to tweak the volume, change songs, or mute sound entirely. Mute buttons
are also found throughout the game outside the menu in various spots for convenience. 

The core game so far only consists of a board of interactive cells. The cells will change color when hovered over, and 
will gain the player's symbol when clicked (if it is the user's turn). Sound effects for hovering and claiming squares
have also been implemented. A turn system between the user and a randomly selecting computer opponent is fully 
implemented. Currently, only the tie scenario is implemented.

A simple post-game screen has been added in the case of a tie, but it is also under construction and lacking features
that it's intended to eventually have. 
 
### TODO

Win/Loss checks

Create a pause between win/loss/tie move and the user being brought the post-game screen

Polish/complete the pre-game / rules display screen, particularly the "no" option

More advanced enemy AI features

post-game resets

keep on making variable cell sizes/spacing based on the amount of squares to render (aka the size of the board)

Save features, stat-tracking features, replay features, etc.

