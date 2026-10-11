# Project Management

This document describes how we organised the Pac-Man project.

## 1. Overview

The project ran for about six weeks. We are a team of two students, and we split the work into two tracks so that each person could work in parallel without blocking the other. We used a Gantt chart (made with onlinegantt.com) to plan the tasks and their dependencies.
We are both part of the Phoenix program. This has helped us stay consistent and meet the weekly deadlines for submitting our project for evaluation. The feedback and discussions with other students during the evaluations have helped us make steady progress and plan the next steps to develop the project in a structured and consistent way.

## 2. Timeline
See the document 'timeline.png' in this folder.

The same plan in table form:

| Period | Task | Who |
|---|---|---|
| 31 Aug – 2 Sep | Parsing (config file) & maze generation (A-Maze-ing package) | Both |
| 2 Sep – 5 Sep | Pacgums & player movements | Both |
| 7 Sep – 11 Sep | Game menu | Marco |
| 7 Sep – 11 Sep | BFS & A* algorithms | Joel |
| 14 Sep – 18 Sep | Game loop | Marco |
| 14 Sep – 18 Sep | Chase mode & frightened mode for ghosts | Joel |
| 21 Sep – 23 Sep | Cheat mode | Marco |
| 21 Sep – 30 Sep | Game testing | Marco |
| 21 Sep – 25 Sep | Testing of game mechanics | Joel |
| 30 Sep – 3 Oct | Levels (at least 10) | Both |
| 5 Oct – 9 Oct | Error testing & documentation | Both |

## 3. Project analysis and choices

We split the project into three phases:

1. **Foundations (together).** Config parsing, maze generation and the basic player/pacgum logic are needed by everything else, so we built them first, as a team.
2. **Parallel work (two tracks).** Marco worked on the user side of the game (menu, game loop, cheat mode). Joel worked on the ghosts' intelligence (BFS, A*, chase and frightened behaviour). These two parts are mostly independent, so we could work at the same time.
3. **Integration and finish (together).** Once the game was playable, we built the levels, then spent the last week on error handling, testing and documentation.

Each track follows the same rhythm: build the feature, then test it. We tested each part right after writing it, so bugs were found early.

## 4. Team organisation

- **Marco**: game menu, game loop, cheat mode, game testing.
- **Joel**: pathfinding (BFS & A*), ghost behaviour (chase / frightened), testing of game mechanics.
- **Both**: parsing, maze generation, pacgums & movements, levels, error testing, documentation.

Decisions were taken together, by discussion. When a task depended on another one, the Gantt chart showed it (arrows between tasks), so we always knew what had to be finished first.

## 5. Risks and mitigation

| Risk | Mitigation |
|---|---|
| The A-Maze-ing package from another group has a different interface or fails | Write a loader that adapts to their interface, handle errors cleanly, and test early (first task of the project) |
| Ghost pathfinding is too slow or too hard to beat | Start with simple BFS, then improve with A*; tune behaviour during testing |
| Delays in one track block the other | Two independent tracks; shared tasks only at the beginning and at the end |
| Not enough time for levels, testing and documentation | Keep a full week at the end for testing and documentation |
| Config file errors crash the game | Robust defaults and clear messages, tested in the final week |

## 6. Testing

- Game mechanics (movement, scoring, lives, ghosts, power pellets) are tested during the second phase.
- The cheat mode (invincibility, level skip, ghost freeze, extra lives) helps us and the reviewers test all levels quickly.
- Final week: error testing (bad config, missing files, generator failures, highscore file problems).
