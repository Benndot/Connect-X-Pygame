# Connect X - Pygame

This is my attempt to create a visual "Connect X" (Think Connect 4, TicTacToe, etc) using the Pygame library. 

The logic and structure of my game is going to be based on an earlier project I made that was text-based and existed
entirely in the command terminal environment. 

This project demonstrates some new concepts for me, such as (simple) animations present in some screens, and well as 
working with more complex gameplay systems under the Pygame library than I have previously. 

## Current State

The app currently has a basic version of everything leading up to the game itself working. Title screen, main menu,
pre-game rock-paper-scissors to determine who goes first. A pre-game rules screen as well. The main menu, while there
in appearance, has no working features beyond moving onward to a game at the present moment. 

The rock-paper-scissors game is complete, and has some fun animated visuals and text. 

A multiple song soundtrack with an options menu to tweak the volume, change songs, or mute sound entirely. Mute buttons
are also found throughout the game outside the menu in various spots for convenience. 

The core game so far only consists of a board of interactive cells. The cells will change color when hovered over, and 
will gain the player's symbol when clicked, however the game logic has not been inserted yet so there's no winning,
losing or tying. 
 
### TODO

Win/Loss checks

Polish/complete the pre-game / rules display screen, particularly the "no" option

More advanced enemy AI features

post-game resets

variable cell sizes based on the playing field (aka accommodate/implement more game modes on-screen)

Save features, stat-tracking features, replay features, etc. 

