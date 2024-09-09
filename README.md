# Checkers Game

This project is an interactive Checkers game developed in Python using the Tkinter library. It provides a graphical user interface for playing Checkers against an AI opponent.

## Features

- Graphical user interface using Tkinter
- Player vs AI gameplay
- Adjustable AI difficulty levels
- Mandatory capture moves
- King piece promotion
- Multi-step captures
- Game rules display

## Requirements

- Python 3.x
- Tkinter library (usually comes pre-installed with Python)

## Installation

1. Clone this repository or download the `checkers.py` file.
2. Ensure you have Python installed on your system.
3. Run the game using the command: python checkers.py

## How to Play

1. Launch the game.
2. Click on a piece to select it.
3. Valid moves will be highlighted on the board.
4. Click on a highlighted square to move your piece.
5. Capture opponent's pieces by jumping over them.
6. The game alternates between player and AI turns.
7. The game ends when one player has no more pieces or valid moves.

## AI Difficulty Levels

You can adjust the AI difficulty level using the dropdown menu:
- Easy
- Medium
- Hard
- Very Hard

## Rules

Click the "Rules" button in the game window to view the rules of Checkers.

## Development

This project was developed by Ferhat SARIKAYA. The game logic and AI are implemented in the `CheckersGame` class, which handles the game state, move validation, and AI decision-making using the Minimax algorithm with alpha-beta pruning.

## Future Improvements

- Add a score display
- Implement an undo move feature
- Add sound effects
- Create a log of moves played

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/fesarikaya/CheckersGame/issues) if you want to contribute.

