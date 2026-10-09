_This project has been created as part of the 42 curriculum by mcarrara, jhenriqu_

# 42-Pac-Man - Ghosts! More ghosts!




# Description

This project is an implementation of the classic Pac-Man created in 1980 by Tōru Iwatani. This project has been created in Python as part of the 42 curriculum. As in the original game, the players progress is based on score and by advancing in levels. We also implemented a cheat mode that will allow us to test the game's functionality without the fun part of actually playing the game as intended.

# Instructions

Python3.10 or later is required to run this project.

``make`` will run the instalation for the requiered dependencies and run the program, if the requiered dependencies are already installed, simply run ``python3 main.py config.json`` to start the game.

Once the game has started, you will be greated by the main screen as displayed below:

![alt text](assets/Screenshot_20261009_133759.png)


Here you can:

* Press SPACE to begin the game

* Press ENTER to review instructions

* View top 10 highest scores

This game also contains a cheat mode use for testing, in order to enable cheat mode go to Instructions and then type in the word "cheat". If cheat mode has been activated succesfully, you will get a message that says "cheat mode ACTIVE"

# Configuration

The game's configurations are found in the ``config.json`` file. This file contains the following configuration details

* h_score - here the address of where the high score persistent data is saved, this file is read to display the top 10 highest scores and written to store the newest score

* lives - indicates the amount of lives you have per game, the default value is 3 lives.

* pacgum - sets the amount of pacgums displayed on the maze.

* points_per_pacgum - set the points per pacgum in the maze.

* points_per_super_pacgum - set the points per super pacgum in the maze.

* points_per_ghost - set the points per ghost eaten in the maze.

* seed - sets the seed for level 1 maze(first maze)

* level_max_time - set the time limit per level.

* level - sets the witdh and hight for each level's maze, 10 levels are defined with decreasing sizes.

# Highscore


# Maze Generation

To generate the maze, we are provided with a mazegenerator packaged based on the A-Maze-ing

# Implementation

# General Software Architecture

# Project Management

![alt text](assets/image.png)

# Resources


