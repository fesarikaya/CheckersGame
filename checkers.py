import tkinter as tk
from tkinter import messagebox
import random
import time

# Constants for the game
BOARD_SIZE = 8
SQUARE_SIZE = 60
PIECE_SIZE = 50
PLAYER_COLOR = "black"
AI_COLOR = "white"
PLAYER_KING_COLOR = "gray"
AI_KING_COLOR = "gold"
AI_DEPTH = 3

class CheckersGame:
    # The CheckersGame class represents the main game logic and user interface for the game of checkers. It handles the initialization of the game window, game board, and user interactions.
    # The class contains methods for drawing the game board, handling player and AI moves, validating moves, capturing pieces, and managing the game flow.
    # It also provides functionality for highlighting valid moves, showing game rules, updating the AI difficulty level, and restarting the game.
    # Overall, the CheckersGame class encapsulates all the necessary components and logic to create a functional and interactive game of checkers.

    def __init__(self):
        # Initialize the game
        self.window = tk.Tk()
        self.window.title("The Checkers Game - Developed By Ferhat SARIKAYA")
        self.canvas = tk.Canvas(self.window, width=BOARD_SIZE * SQUARE_SIZE, height=BOARD_SIZE * SQUARE_SIZE)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_player_move)
        self.selected_piece = None

        # Create a dropdown menu for difficulty levels
        self.difficulty_var = tk.StringVar(self.window)
        self.difficulty_var.set("Easy")
        difficulty_options = ["Easy", "Medium", "Hard", "Very Hard"]
        difficulty_menu = tk.OptionMenu(self.window, self.difficulty_var, *difficulty_options)
        difficulty_menu.pack()
        self.difficulty_var.trace("w", self.update_ai_depth)

        # Create the initial board
        self.board = [
            ["", AI_COLOR, "", AI_COLOR, "", AI_COLOR, "", AI_COLOR],
            [AI_COLOR, "", AI_COLOR, "", AI_COLOR, "", AI_COLOR, ""],
            ["", AI_COLOR, "", AI_COLOR, "", AI_COLOR, "", AI_COLOR],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            [PLAYER_COLOR, "", PLAYER_COLOR, "", PLAYER_COLOR, "", PLAYER_COLOR, ""],
            ["", PLAYER_COLOR, "", PLAYER_COLOR, "", PLAYER_COLOR, "", PLAYER_COLOR],
            [PLAYER_COLOR, "", PLAYER_COLOR, "", PLAYER_COLOR, "", PLAYER_COLOR, ""]
        ]

        # Create a button to show the rules
        rules_button = tk.Button(self.window, text="Rules", command=self.show_rules)
        rules_button.pack()

    def start(self):
        # Start the game
        self.draw_board()
        self.window.mainloop()

    def draw_board(self):
        # Draw the game board
        self.canvas.delete("all")
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x1 = col * SQUARE_SIZE
                y1 = row * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE
                if (row + col) % 2 == 0:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="DarkOrange")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="chocolate")
                if self.board[row][col] != "":
                    piece_color = self.board[row][col]
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill=piece_color)

    def handle_player_move(self, event):
        # The method is responsible for handling the player's move in the game of checkers.
        # It is triggered when the player clicks on a square on the game board.
        # The method first determines if the player is selecting a piece to move or making a move with a previously selected piece.
        # If a piece is being selected, it highlights the valid moves and mandatory captures for that piece.
        # If a move is being made, it validates the move and performs the necessary actions, such as capturing opponent pieces and promoting the piece to a king if applicable.
        # The method also handles the case when the player must make a mandatory capture move.
        # After the player's move is completed, it checks if the game is over and either switches to the AI's turn or ends the game.

        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE
        if self.selected_piece is None:
            if self.board[row][col] == PLAYER_COLOR or self.board[row][col] == PLAYER_KING_COLOR:
                self.selected_piece = (row, col)
                self.draw_board()
                valid_moves, mandatory_captures = self.get_valid_moves(PLAYER_COLOR)
                self.highlight_moves(self.selected_piece)
                self.highlight_mandatory_captures(PLAYER_COLOR)
        else:
            move = (self.selected_piece, (row, col))
            valid_moves, mandatory_captures = self.get_valid_moves(PLAYER_COLOR)
            if mandatory_captures:
                captures = [capture for capture in mandatory_captures if capture[0] == self.selected_piece]
                if captures:
                    if move in [capture[:2] for capture in captures]:
                        captured_positions = next(capture[2] for capture in captures if capture[:2] == move)
                        while True:
                            self.board = self.make_move(move + (captured_positions,))
                            self.draw_board()
                            self.window.update()
                            time.sleep(1)  # Add a delay of 1 second between each capture move

                            # Check if the piece has become a king by capturing an opponent's king
                            if self.board[move[1][0]][move[1][1]] == PLAYER_KING_COLOR:
                                break

                            valid_moves, mandatory_captures = self.get_valid_moves(PLAYER_COLOR)
                            filtered_captures = [capture for capture in mandatory_captures if capture[0] == move[1]]
                            if filtered_captures:
                                move = filtered_captures[0][:2]
                                captured_positions = filtered_captures[0][2]
                            else:
                                break
                        self.selected_piece = None
                        if self.is_game_over():
                            self.show_game_over()
                        else:
                            self.window.after(100, self.handle_ai_move)
                    else:
                        messagebox.showwarning("Invalid Move", "You must make a capture move!")
                        self.selected_piece = None
                        self.draw_board()
                        self.highlight_mandatory_captures(PLAYER_COLOR)
                else:
                    messagebox.showwarning("Invalid Move", "You must make a capture move!")
                    self.selected_piece = None
                    self.draw_board()
                    self.highlight_mandatory_captures(PLAYER_COLOR)
            elif move in valid_moves:
                self.board = self.make_move(move)
                self.draw_board()
                self.selected_piece = None
                if self.is_game_over():
                    self.show_game_over()
                else:
                    self.window.after(100, self.handle_ai_move)
            else:
                self.selected_piece = None
                self.draw_board()
                self.highlight_mandatory_captures(PLAYER_COLOR)

    def minimax(self, depth, alpha, beta, maximizing_player, moves):
        # The method helps determine the best move for a player by evaluating all possible moves and their outcomes, assuming that the opponent plays optimally.
        # The algorithm recursively explores the game tree, alternating between maximizing the score for the current player and minimizing the score for the opponent.

        if depth == 0 or self.is_game_over():
            return self.evaluate_board(), None

        if maximizing_player:
            max_eval = float('-inf')
            best_move = None
            for move in moves:
                new_board = self.make_move(move)
                valid_moves, mandatory_captures = self.get_valid_moves(PLAYER_COLOR)
                if mandatory_captures:
                    eval = self.minimax(depth - 1, alpha, beta, False, mandatory_captures)[0]
                else:
                    eval = self.minimax(depth - 1, alpha, beta, False, valid_moves)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in moves:
                new_board = self.make_move(move)
                valid_moves, mandatory_captures = self.get_valid_moves(AI_COLOR)
                if mandatory_captures:
                    eval = self.minimax(depth - 1, alpha, beta, True, mandatory_captures)[0]
                else:
                    eval = self.minimax(depth - 1, alpha, beta, True, valid_moves)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def evaluate_board(self):
        # The method is used to assess the current state of the game board and assign a numeric score to it.
        # It takes into account various factors, such as the number of remaining pieces for each player, the number of king pieces, and potentially other strategic considerations.
        # The score is calculated based on the difference between the AI player's pieces and the human player's pieces, as well as a weighted value for the king pieces.
        # This evaluation helps the Minimax algorithm determine the desirability of a particular board configuration and guides the decision-making process for the AI player.
        # The higher the score, the more favourable the board state is considered for the AI player.

        player_pieces = sum(row.count(PLAYER_COLOR) + row.count(PLAYER_KING_COLOR) for row in self.board)
        ai_pieces = sum(row.count(AI_COLOR) + row.count(AI_KING_COLOR) for row in self.board)
        player_kings = sum(row.count(PLAYER_KING_COLOR) for row in self.board)
        ai_kings = sum(row.count(AI_KING_COLOR) for row in self.board)

        # Calculate the score based on piece count and king count
        score = (ai_pieces - player_pieces) + (ai_kings * 0.5 - player_kings * 0.5)
        return score

    def handle_ai_move(self):
        # The method is responsible for handling the AI's moves in the game of checkers. It is called after the player's move is completed.
        # The method first checks if the game is over. If not, it retrieves the valid moves and mandatory captures for the AI player.
        # If there are mandatory captures available, it randomly selects one of them and performs the capture move.
        # If there are no mandatory captures, it randomly selects a valid move.
        # The method also handles the case when the AI captures an opponent's king, promoting its own piece to a king.
        # After the AI's move is completed, it updates the game board, adds a delay for visual effect, and checks if the game is over.
        # If the game is over, it calls the show_game_over method to display the result.

        if not self.is_game_over():
            valid_moves, mandatory_captures = self.get_valid_moves(AI_COLOR)
            if mandatory_captures:
                ai_move = self.minimax(AI_DEPTH, float('-inf'), float('inf'), True, mandatory_captures)[1]
                captured_positions = ai_move[2]
                while True:
                    self.board = self.make_move(ai_move)
                    self.draw_board()
                    self.window.update()
                    time.sleep(1)  # Add a delay of 1 second between each capture move

                    # Check if the piece has become a king by capturing an opponent's king
                    if self.board[ai_move[1][0]][ai_move[1][1]] == AI_KING_COLOR:
                        break

                    valid_moves, mandatory_captures = self.get_valid_moves(AI_COLOR)
                    filtered_captures = [capture for capture in mandatory_captures if capture[0] == ai_move[1]]
                    if filtered_captures:
                        ai_move = self.minimax(AI_DEPTH, float('-inf'), float('inf'), True, filtered_captures)[1]
                        captured_positions = ai_move[2]
                    else:
                        break
            else:
                ai_move = self.minimax(AI_DEPTH, float('-inf'), float('inf'), True, valid_moves)[1]
                if ai_move is not None:
                    self.board = self.make_move(ai_move)
                    self.draw_board()
                    self.window.update()
                    time.sleep(1)  # Add a delay of 1 second for AI's move
            if self.is_game_over():
                self.show_game_over()

    def get_valid_moves(self, player_color):
        # The method is responsible for retrieving all the valid moves and mandatory captures for a given player (either the human player or the AI player) in the game of checkers.
        # It iterates over each square on the game board and checks if the square contains a piece belonging to the specified player.
        # For each piece, it calls the get_valid_captures and get_valid_moves_for_piece methods to determine the valid capture moves and regular moves, respectively.
        # The method returns two lists: one containing all the valid regular moves and another containing all the mandatory capture moves.
        # This information is used by other methods to highlight the available moves for the player and to validate the player's move.

        valid_moves = []
        mandatory_captures = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == player_color or self.board[row][col] == self.get_king_color(player_color):
                    captures = self.get_valid_captures(row, col)
                    if captures:
                        mandatory_captures.extend(captures)
                    moves = self.get_valid_moves_for_piece(row, col)
                    valid_moves.extend(moves)

        return valid_moves, mandatory_captures

    def get_valid_moves_for_piece(self, row, col):
        # The method is responsible for retrieving the valid regular moves for a specific piece on the game board.
        # It takes the row and column coordinates of the piece as input.
        # The method first determines the color of the piece and whether it is a regular piece or a king.
        # Based on the piece color, it defines the possible move directions. For a regular piece, it can move diagonally forward, while a king piece can move diagonally both forward and backward.
        # The method then checks each possible move direction and adds the move to the list of valid moves if the destination square is empty and within the bounds of the game board.
        # Additionally, it calls the get_valid_captures method to retrieve any valid capture moves for the piece and appends them to the list of valid moves.
        # The method returns the complete list of valid moves for the given piece.

        valid_moves = []
        piece_color = self.board[row][col]
        is_king = piece_color in [PLAYER_KING_COLOR, AI_KING_COLOR]

        # Regular piece movement
        if piece_color == PLAYER_COLOR:
            directions = [(-1, -1), (-1, 1)]
        else:
            directions = [(1, -1), (1, 1)]

        for d_row, d_col in directions:
            new_row, new_col = row + d_row, col + d_col
            if self.is_valid_position(new_row, new_col) and self.board[new_row][new_col] == "":
                valid_moves.append(((row, col), (new_row, new_col)))

        # King piece movement
        if is_king:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for d_row, d_col in directions:
                new_row, new_col = row + d_row, col + d_col
                if self.is_valid_position(new_row, new_col) and self.board[new_row][new_col] == "":
                    valid_moves.append(((row, col), (new_row, new_col)))

        # Capture moves
        captures = self.get_valid_captures(row, col)
        valid_moves.extend(captures)

        return valid_moves

    def get_valid_captures(self, row, col):
        # The method is responsible for retrieving the valid capture moves for a specific piece on the game board.
        # It takes the row and column coordinates of the piece as input.
        # The method first determines the color of the piece, whether it is a regular piece or a king, and the color of the opponent's pieces.
        # Based on the piece's color and type, it defines the possible capture directions.
        # It then checks each possible capture direction to see if there is an opponent's piece in the adjacent square and an empty square beyond it.
        # If a valid capture is found, it adds the capture move to the list of captures and recursively calls the get_valid_captures_for_board method to check for multi-step captures.
        # The recursive call is made on a copy of the game board, with the piece moved to the captured position.
        # The method returns the complete list of valid capture moves for the given piece, including any multi-step captures.

        captures = []
        piece_color = self.board[row][col]
        is_king = piece_color in [PLAYER_KING_COLOR, AI_KING_COLOR]
        opponent_piece, opponent_king = (
            AI_COLOR, AI_KING_COLOR) if piece_color in [PLAYER_COLOR, PLAYER_KING_COLOR] else (
            PLAYER_COLOR, PLAYER_KING_COLOR)

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] if is_king else [(-1, -1), (-1, 1)] if piece_color == PLAYER_COLOR else [(1, -1), (1, 1)]

        for d_row, d_col in directions:
            new_row, new_col = row + d_row, col + d_col
            if self.is_valid_position(new_row, new_col) and self.board[new_row][new_col] in [opponent_piece, opponent_king]:
                jump_row, jump_col = new_row + d_row, new_col + d_col
                if self.is_valid_position(jump_row, jump_col) and self.board[jump_row][jump_col] == "":
                    captured_positions = [(new_row, new_col)]
                    captures.append(((row, col), (jump_row, jump_col), captured_positions))
                    # Check for multi-step captures
                    board_copy = [row[:] for row in self.board]
                    board_copy[jump_row][jump_col] = piece_color
                    board_copy[new_row][new_col] = ""
                    board_copy[row][col] = ""
                    further_captures = self.get_valid_captures_for_board(board_copy, jump_row, jump_col)
                    for capture in further_captures:
                        captures.append(((row, col), capture[1], captured_positions + capture[2]))

        return captures

    def get_valid_captures_for_board(self, board, row, col):
        # The method is a helper method used by the get_valid_captures method to retrieve the valid capture moves for a specific piece on a given game board configuration.
        # It takes the game board, row, and column coordinates of the piece as input.
        # The purpose of this method is to handle multi-step captures. When a piece makes a capture move, the method recursively calls itself on the updated game board to check if further captures are possible from the new position.
        # It follows the same logic as the get_valid_captures method to determine the possible capture directions and validate the captures.
        # The method returns the list of valid capture moves for the piece on the given game board configuration, allowing the get_valid_captures method to construct the complete list of capture moves, including multi-step captures.

        captures = []
        piece_color = board[row][col]
        is_king = piece_color in [PLAYER_KING_COLOR, AI_KING_COLOR]
        opponent_piece, opponent_king = (
            AI_COLOR, AI_KING_COLOR) if piece_color in [PLAYER_COLOR, PLAYER_KING_COLOR] else (
            PLAYER_COLOR, PLAYER_KING_COLOR)

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] if is_king else [(-1, -1), (-1, 1)] if piece_color == PLAYER_COLOR else [(1, -1), (1, 1)]

        for d_row, d_col in directions:
            new_row, new_col = row + d_row, col + d_col
            if self.is_valid_position(new_row, new_col) and board[new_row][new_col] in [opponent_piece, opponent_king]:
                jump_row, jump_col = new_row + d_row, new_col + d_col
                if self.is_valid_position(jump_row, jump_col) and board[jump_row][jump_col] == "":
                    captured_positions = [(new_row, new_col)]
                    captures.append(((row, col), (jump_row, jump_col), captured_positions))
                    # Check for multi-step captures
                    board_copy = [row[:] for row in board]
                    board_copy[jump_row][jump_col] = piece_color
                    board_copy[new_row][new_col] = ""
                    board_copy[row][col] = ""
                    further_captures = self.get_valid_captures_for_board(board_copy, jump_row, jump_col)
                    for capture in further_captures:
                        captures.append(((row, col), capture[1], captured_positions + capture[2]))

        return captures

    def make_move(self, move):
        # The method is responsible for executing a move on the game board. It takes a move tuple as input, which contains the starting position, ending position, and any captured positions.
        # The method first retrieves the necessary information from the move tuple, such as the starting row and column, ending row and column, and the color of the piece being moved.
        # It then creates a new game board by making a copy of the current board.
        # The method updates the new board by moving the piece from the starting position to the ending position and removing any captured pieces from the board.
        # Additionally, it checks if the moved piece should be promoted to a king based on its ending position or if it captured an opponent's king.
        # The method returns the updated game board after the move has been executed.

        start_row, start_col = move[0]
        end_row, end_col = move[1]
        captured_positions = move[2] if len(move) > 2 else []
        piece_color = self.board[start_row][start_col]
        new_board = [row[:] for row in self.board]
        new_board[end_row][end_col] = piece_color
        new_board[start_row][start_col] = ""

        # Check for king conversion
        if piece_color == PLAYER_COLOR and (end_row == 0 or any(self.board[pos[0]][pos[1]] == AI_KING_COLOR for pos in captured_positions)):
            new_board[end_row][end_col] = PLAYER_KING_COLOR
        elif piece_color == AI_COLOR and (end_row == BOARD_SIZE - 1 or any(self.board[pos[0]][pos[1]] == PLAYER_KING_COLOR for pos in captured_positions)):
            new_board[end_row][end_col] = AI_KING_COLOR

        # Remove captured pieces
        for captured_row, captured_col in captured_positions:
            new_board[captured_row][captured_col] = ""

        return new_board

    def is_valid_position(self, row, col):
        # The method is a simple helper method that checks if a given position, specified by row and column coordinates, is valid on the game board.
        # It takes the row and column as input and returns a boolean value indicating whether the position is within the bounds of the game board.
        # The method checks if the row and column values are greater than or equal to 0 and less than the size of the game board (BOARD_SIZE).

        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def get_king_color(self, player_color):
        # The get_king_color method is a helper method that returns the corresponding king color for a given player color.
        # It takes the player color as input and returns the king color based on the player.
        # If the input player color is PLAYER_COLOR (black), the method returns PLAYER_KING_COLOR (gray), indicating the color of the white player's king pieces.
        # Similarly, if the input player color is AI_COLOR (white), the method returns AI_KING_COLOR (gold), indicating the color of the black player's king pieces.
        # This method is used to determine the appropriate king color when promoting a piece to a king during the game.
        if player_color == PLAYER_COLOR:
            return PLAYER_KING_COLOR
        elif player_color == AI_COLOR:
            return AI_KING_COLOR

    def highlight_moves(self, selected_piece):
        # The method is responsible for visually highlighting the squares on the game board where a selected piece can make valid moves.
        # It takes the selected piece's position as input.
        # The method first retrieves the valid moves for the selected piece by calling the get_valid_moves_for_piece method.
        # It then iterates over each valid move and calculates the corresponding square coordinates on the game board.
        # Using the canvas object, the method creates a yellow rectangle with a stippled pattern on each valid move square.
        # This visual indication helps the player identify the possible moves for the selected piece.

        valid_moves = self.get_valid_moves_for_piece(selected_piece[0], selected_piece[1])
        for move in valid_moves:
            end_row, end_col = move[1]
            x1 = end_col * SQUARE_SIZE
            y1 = end_row * SQUARE_SIZE
            x2 = x1 + SQUARE_SIZE
            y2 = y1 + SQUARE_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="yellow", stipple="gray50")

    def highlight_mandatory_captures(self, player_color):
        # The method is responsible for visually highlighting the pieces on the game board that have mandatory capture moves available.
        # It takes the player's color as input.
        # The method retrieves the mandatory capture moves for the specified player by calling the get_valid_moves method.
        # It then iterates over each mandatory capture move and extracts the starting position of the piece.
        # Using the canvas object, the method creates a yellow outline rectangle around each piece that has a mandatory capture move.
        # This visual indication helps the player identify the pieces that must make a capture move during their turn.

        _, mandatory_captures = self.get_valid_moves(player_color)
        for move in mandatory_captures:
            start_row, start_col = move[0]
            x1 = start_col * SQUARE_SIZE
            y1 = start_row * SQUARE_SIZE
            x2 = x1 + SQUARE_SIZE
            y2 = y1 + SQUARE_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=4)

    def is_game_over(self):
        # Check if the game is over
        player_pieces = sum(row.count(PLAYER_COLOR) + row.count(PLAYER_KING_COLOR) for row in self.board)
        ai_pieces = sum(row.count(AI_COLOR) + row.count(AI_KING_COLOR) for row in self.board)
        game_over = False
        if player_pieces == 0 or ai_pieces == 0:
            game_over = True

        return game_over

    def show_game_over(self):
        # Show the game over message
        player_pieces = sum(row.count(PLAYER_COLOR) + row.count(PLAYER_KING_COLOR) for row in self.board)
        ai_pieces = sum(row.count(AI_COLOR) + row.count(AI_KING_COLOR) for row in self.board)

        if player_pieces == 0:
            result = "You lost!"
        elif ai_pieces == 0:
            result = "You won!"
        else:
            player_moves = self.get_valid_moves(PLAYER_COLOR)
            if player_pieces > 0 and len(player_moves[0]) == 0 and len(player_moves[1]) == 0:
                result = "You lost!"
            else:
                result = "You won!"

        self.canvas.delete("all")
        self.canvas.create_text(BOARD_SIZE * SQUARE_SIZE // 2, BOARD_SIZE * SQUARE_SIZE // 2, text=result,
                                font=("Arial", 32), fill="blue")
        self.window.after(2000, self.restart_game)

    def update_ai_depth(self, *args):
        # Update AI depth based on selected difficulty level
        global AI_DEPTH
        selected_difficulty = self.difficulty_var.get()
        if selected_difficulty == "Easy":
            AI_DEPTH = 3
        elif selected_difficulty == "Medium":
            AI_DEPTH = 5
        elif selected_difficulty == "Hard":
            AI_DEPTH = 7
        elif selected_difficulty == "Very Hard":
            AI_DEPTH = 10
        self.restart_game()

    def restart_game(self):
        # Restart the game
        self.board = [
            ["", AI_COLOR, "", AI_COLOR, "", AI_COLOR, "", AI_COLOR],
            [AI_COLOR, "", AI_COLOR, "", AI_COLOR, "", AI_COLOR, ""],
            ["", AI_COLOR, "", AI_COLOR, "", AI_COLOR, "", AI_COLOR],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            [PLAYER_COLOR, "", PLAYER_COLOR, "", PLAYER_COLOR, "", PLAYER_COLOR, ""],
            ["", PLAYER_COLOR, "", PLAYER_COLOR, "", PLAYER_COLOR, "", PLAYER_COLOR],
            [PLAYER_COLOR, "", PLAYER_COLOR, "", PLAYER_COLOR, "", PLAYER_COLOR, ""]
        ]
        self.draw_board()

    def show_rules(self):
        # Show rules in a popup window
        rules_window = tk.Toplevel(self.window)
        rules_window.title("Checkers Rules")
        rules_text = tk.Text(rules_window, width=80, height=20)
        rules_text.pack()
        rules_text.insert(tk.END, "1. The game is played on an 8x8 checkered board.\n")
        rules_text.insert(tk.END,
                          "2. Each player starts with 12 pieces, placed on the dark squares of the three rows closest to them.\n")
        rules_text.insert(tk.END,
                          "3. Players take turns moving their pieces diagonally forward to an adjacent empty square.\n")
        rules_text.insert(tk.END,
                          "4. If a player's piece is adjacent to an opponent's piece, and the square beyond the opponent's piece is empty, the player must jump over and capture the opponent's piece.\n")
        rules_text.insert(tk.END, "5. If a player can make multiple captures in a single turn, they must do so.\n")
        rules_text.insert(tk.END,
                          "6. If a piece reaches the opposite end of the board, it is crowned as a king and can move both forward and backward.\n")
        rules_text.insert(tk.END,
                          "7. If a piece captures a king, it is immediately crowned as a king (regicide).\n")
        rules_text.insert(tk.END,
                          "8. The game ends when one player captures all of the opponent's pieces or when neither player can make a move.\n")


if __name__ == "__main__":
    game = CheckersGame()
    game.start()