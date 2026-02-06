import copy # Requirement: Used to clone the board for the undo/history logic [cite: 44, 96]
import random # Requirement: Used for random game events [cite: 33, 43]

class GoGame:
    """
    This class handles the core logic of the Go game, including board management,
    captures, and rule enforcement. 
    """
    def __init__(self, size=19):
        self.size = size 
        # Requirement: Lists to store game state [cite: 44, 96]
        self.board = [['.' for _ in range(size)] for _ in range(size)] #self.board, you are telling the computer: "I want this specific game to have its own private board made of dots."
        self.current_player = 'X'  # X for Black, O for White
        self.history = []  # Stores (board, player) tuples for undoing [cite: 44, 62]
        self.captured_stones = {'X': 0, 'O': 0} # Track capture scores [cite: 39, 63]
        self.pass_count = 0 # Track consecutive passes to end the game [cite: 60]
        self.first_move_made = False # Tracks if the random start has occurred [cite: 39, 63]

    def random_start(self):
        """
        Requirement: Randomness. 
        Automatically places the first stone for Player X at a random location. [cite: 33, 43, 67]
        """
        r = random.randint(0, self.size - 1) #row randomized from 0-18
        c = random.randint(0, self.size - 1) #column randomized from 0-18
        
        # Save state before placing the random stone
        self.history.append((copy.deepcopy(self.board), self.current_player))
        
        self.board[r][c] = 'X'
        print(f"\n🎲 RANDOM START: Player X's first stone was placed at ({r}, {c})")
        
        self.current_player = 'O' # Pass turn to White
        self.first_move_made = True # Ensure this only happens once [cite: 41]

    def display_board(self):
        """Prints the current state of the board in a clean grid format. """
        header = "    " + "".join([f"{i:^3}" for i in range(self.size)])
        print(header)
        for r in range(self.size):
            row_str = "".join([f"{self.board[r][c]:^3}" for c in range(self.size)])
            print(f"{r:2} {row_str}")

    def display_score(self):
        """Requirement: Output game status to the user. """
        print("\n" + "="*30)#new line and 30 equals signs
        print(f"SCOREBOARD:")
        print(f"Player X (Black): {self.captured_stones['X']} stones captured")
        print(f"Player O (White): {self.captured_stones['O']} stones captured")
        print("="*30 + "\n")

    def undo_move(self):
        """Requirement: Meaningful player choice. Reverts to one turn ago. """
        if len(self.history) > 0:
            old_board, old_player = self.history.pop() #.pop() (Taking the last photo out)
            #Once the computer has that "last photo" in its hand, it needs to update the "real" game to match it.
            self.board = old_board #redefine
            self.current_player = old_player
            print(f"Undo successful! It is now Player {self.current_player}'s turn.")
        else:
            print("Nothing to undo!")

    
    def get_neighbors(self, r, c):
        """Helper to find adjacent intersections. """
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc #dr and dc stand for "Change in Row" and "Change in Column."
                                    #nr and nc stand for "New Row" and "New Column."
                                    
            if 0 <= nr < self.size and 0 <= nc < self.size:#safety check. It asks: "Is this neighbor actually on the board?"
                neighbors.append((nr, nc))
        return neighbors
        """If you are at Row 5, Column 5:
            It takes the first step (-1, 0).
            nr = 5 + (-1) which is 4.
            nc = 5 + 0 which is 5.
            Your first neighbor is (4, 5).
            append adds that neighbor to the list of neighbors.
            
            """
    def get_group(self, r, c):#finds every single stone that belongs to that specific army.
        """Finds all connected stones of the same color. """
        color = self.board[r][c]#Find all stone of the same color of the corrdinate given
        group, stack = set([(r, c)]), [(r, c)] #This is our official list of everyone in the army. list of stones we need to check. We start by putting our first stone on this list.
        #a set is a special collection that doesn't allow duplicates. This is like a guest list where you can't write the same name twice.
        while stack:#Imagine you are trying to find everyone invited to a party, but you only have one name to start with.
            curr_r, curr_c = stack.pop()#You take a name off your stack
            for nr, nc in self.get_neighbors(curr_r, curr_c):#You look at that person's neighbors
                if self.board[nr][nc] == color and (nr, nc) not in group:#You ask each neighbor: "Are you the same color as us?"
                    group.add((nr, nc))#add to group
                    stack.append((nr, nc))#You also put them on the stack (the To-Do list) because now you need to go check their neighbors too.
        return group

    def get_liberties(self, group):
        """Counts empty adjacent spaces for a group."""
        liberties = set()
        for r, c in group:#The computer looks at every single stone in the army we found earlier.
            for nr, nc in self.get_neighbors(r, c):#For each of those stones, the computer reaches out and touches its neighbors (North, South, East, and West).
                if self.board[nr][nc] == '.':
                    liberties.add((nr, nc))
        return len(liberties)
    

    def handle_captures(self, opponent_color):
        """Checks for and removes groups with zero liberties. """
        total_captured = 0
        for r in range(self.size):
            for c in range(self.size):#going row-by-row and column-by-column until every single square on the board has been checked.
                if self.board[r][c] == opponent_color:#The computer only stops to check a square if it contains an "enemy" stone. If it's an empty dot or your own stone, it keeps moving.
                    group = self.get_group(r, c)#see how big this group of stones is.
                    if self.get_liberties(group) == 0:#If the answer is 0, the stones have "suffocated."
                        total_captured += len(group)#It counts how many stones were in that army and adds them to the score.
                        for gr, gc in group:
                            self.board[gr][gc] = '.'#It loops through every stone in that specific group and turns them back into dots (empty spaces).
        return total_captured

    def play_move(self, r, c):
        """Validates and executes a player's move"""
        if not (0 <= r < self.size and 0 <= c < self.size) or self.board[r][c] != '.':
            return False, "Invalid position!"

        self.history.append((copy.deepcopy(self.board), self.current_player))#adds duplicate of current board and player to history before making move
        self.board[r][c] = self.current_player#self.current_player is holding a stamp. If it is Black's turn, the stamp says 'X'.
        opponent = 'O' if self.current_player == 'X' else 'X'
        
        self.captured_stones[self.current_player] += self.handle_captures(opponent)
        #takes opponet stone and add score to current player
        self.current_player = opponent
        self.pass_count = 0
        return True, "Success"

def main():
    """Repeated gameplay using a loop. """
    game = GoGame(19)
    
    print("--- WELCOME TO TEXT-GO ---")
    print("Inspiration: Classic Go")
    print("Instructions:")
    print("- To play: Enter row and column (e.g., '5 5')")
    print("- To undo: Enter 'u'")
    print("- To see score: Enter 's'")
    print("- To pass: Enter 'p'")
    print("- To quit: Enter 'q'")
#instructions doesn't repeat, game repeats until false or break
    while True:
        # Step 1: Handle Random Start if it's the very first turn 
        if not game.first_move_made:
            game.random_start()
            continue # Re-loop to show the board with the new random stone
            
        game.display_board()
        game.display_score()
        print(f"Turn: Player {game.current_player}")
        user_input = input("Enter command: ").strip().lower()

        if user_input == 'q':
            break
        elif user_input == 's':
            game.display_score()
        elif user_input == 'u':
            game.undo_move()
        elif user_input == 'p':
            game.pass_count += 1
            game.current_player = 'O' if game.current_player == 'X' else 'X'
            print("Player passed.")
            if game.pass_count >= 2: # End condition [cite: 60]
                print("\nGAME OVER!")
                game.display_score()
                if game.captured_stones['X'] > game.captured_stones['O']:
                    print("🎉 Player X wins!")
                elif game.captured_stones['O'] > game.captured_stones['X']:
                    print("🎉 Player O wins!")
                else:
                    print("It's a draw!")
                break
        else:
            try:
                r, c = map(int, user_input.split())#separate 5 10 to 5 and 10, map int -> number
                #map == "Use the int tool on every item that comes through." map takes that list and runs the int() function on every piece inside.
                success, msg = game.play_move(r, c) #The main loop asks: "Hey play_move, I have a Row r and a Column c. Can you put a stone there?"
                #play move returns two things: success (True/False) and a message
                if not success: #if not success: is like saying, "If the success variable is False, do the following."
                    print(f"❌ Error: {msg}")
            except (ValueError, IndexError):
                print("❌ Invalid input. Use 'row col' or a command like 'p'.")
#If the try succeeds: The computer skips the except block entirely and moves on to play the game.
#If the try fails: The computer immediately stops what it's doing in the try block and jumps down to the except block to execute the safety instructions.
if __name__ == "__main__":
    main()