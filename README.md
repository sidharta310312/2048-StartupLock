# 2048
## What is this program?
A simple 2048 game with cool GUI transition effects, data-saving system to save your game inside your computer, and even a feature where you can **lock your own computer.**

The source code is entirely written in Python. (Only supportable in Windows)

## The game itself
This project is just a recreation of the classic 2048 game. But you can change the board size to anything you want as long as the width and height values are inbetween 2 and 10
(2x2, 4x4, 10x10, 7x8, 6x7, and much more! There are 81 possible size combinations)

You can also add custom tile colors, simply head to line 125 and you'll see a variable tuple named _blockColors_. The only tiles with proper color assignments are tile 2-128 (or 1 to 7 in base 2 logarithmic value). You can add more colors for more tiles in RGB value

(For example, if you wan't to set tile 256 to Green, set the 8th item of the list (index = 7) to (0, 255, 0) which is the color Green in RGB. Why specifically the 8th item? Because the base-2 logarithmic value of 256 is 8)

Any other tile without proper color assignments will be colored black, alias (0, 0, 0) in RGB.

## Data-saving system
The game heavily requires Drive D (D:/) to save your games, but the game can still run even if you don't have Drive D.
But if you don't have Drive D (only C:/ and anything else), don't worry! Simply go to line 32 and change the _saveFile_drive_ variable to any drive you own (that isn't C:/)

FOR EXAMPLE : You have no Drive D and your only drives are C:/ and F:/, if you want to enable datasaving systems for your computer, change _saveFile_drive_ value from "D" to "F"

## Startup Lock Mode
Now this is where things get interesting.
You can enable Startup Lock Mode by going to the home page of the game, then do the Konami code sequence (Up up down down left right left right A B Enter) to open the settings.

### _What even is the Startup Lock Mode?_
This is a hidden feature in the game where you can **lock your own computer upon startup** when this setting is enabled. To unlock the computer, you will have to get a specific score in 2048. If you fail = computer shutdown, if you succeed = you unlock your computer. You can apply this to your friend's computer as long as your friend uses Windows OS

The Startup Lock Mode settings has 2 primary options : Score Goal and Time Limit:

1. Score Goal : Set a specific score goal you need to get to unlock your computer, options range from 128 to 1024 (or in base-2 logarithmic values = 7 to 10)
2. Time Limit : You can set the time limit from 1 to 5 minutes. If the user **runs out of time** while trying to beat the 2048 puzzle, their computer will be **shutdowned** (Adding a timer is completely optional)

## Libraries used (Built-in and Non built-in)
The program consists of 14 built-in libraries and 2 non built-in libraries (pygame and requests)

If you don't have those 2 required non built-in libraries, simply install PIP (Python's package installer) and run this in your terminal window :
pip install pygame
pip install requests

## Extra message
If you like my project, thank you for appreciating it. If you don't, feel free to check out other projects I've made or other people's projects (maybe you'd like one of them!)

Feel free to modify and rewrite the source code, afterall, GitHub is a place where you share open source free code.

25/06/2026
