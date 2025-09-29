import os
import json
import random

# File to store player progress
SAVE_FILE = "progress.json"

def load_progress():
    """
    Load player progress from a file.
    If the file does not exist, initialize default progress.
    """
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            progress = json.load(f)
    else:
        progress = {
            "current_room": "start",
            "inventory": [],
            "score": 0,
            "moves": []
        }
    return progress

def save_progress(progress):
    """
    Save the current player progress to a file.
    """
    with open(SAVE_FILE, "w") as f:
        json.dump(progress, f)

def start_room(progress):
    """
    The starting room offers three paths:
    left -> puzzle_room, right -> treasure_room, center -> secret_room.
    """
    print("\n[Start Room]")
    print("You find yourself in a mysterious hall with three pathways: left, right, and center.")
    
    choice = input("Choose a path (left/right/center): ").strip().lower()
    progress["moves"].append(f"Start room: chose {choice}")
    
    if choice == "left":
        progress["current_room"] = "puzzle_room"
    elif choice == "right":
        progress["current_room"] = "treasure_room"
    elif choice == "center":
        progress["current_room"] = "secret_room"
    else:
        print("Invalid choice. Please try again.")
        return start_room(progress)
    
    return progress

def puzzle_room(progress):
    """
    The puzzle room challenges the player with two puzzles.
    First, a riddle; then a math puzzle.
    """
    print("\n[Puzzle Room]")
    print("You enter a room with a locked door. A mysterious voice challenges you with two puzzles.")
    
    # Puzzle 1: Riddle
    while True:
        answer = input("Puzzle 1 - Riddle: What has keys but can't open locks? ").strip().lower()
        if answer == "piano":
            print("Correct! Now onto the next puzzle.")
            break
        else:
            print("Incorrect. Try again.")
    
    # Puzzle 2: Math Puzzle
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    correct = a + b
    while True:
        try:
            user_answer = int(input(f"Puzzle 2 - Math: What is {a} + {b}? "))
            if user_answer == correct:
                print("Correct! The door unlocks.")
                progress["score"] += 10  # Increase score for solving puzzles
                break
            else:
                print("Incorrect. Try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    progress["moves"].append("Solved puzzles in puzzle_room")
    progress["current_room"] = "treasure_room"  # Proceed to the treasure room
    return progress

def secret_room(progress):
    """
    The secret room is a hidden path with its own challenge.
    The player can choose to inspect artifacts and solve a math riddle.
    """
    print("\n[Secret Room]")
    print("You have discovered a hidden passage leading to a secret room filled with ancient artifacts.")
    
    while True:
        choice = input("Do you want to (inspect) the artifacts or (ignore) them and go back? ").strip().lower()
        if choice == "inspect":
            print("You inspect the artifacts and find a mysterious scroll with a math riddle: 'Solve: 12 * 3 - 5'")
            try:
                answer = int(input("What is your answer? "))
                if answer == (12 * 3 - 5):  # 31 is the correct answer
                    print("Correct! The scroll grants you an enchanted item.")
                    progress["inventory"].append("Enchanted Scroll")
                    progress["score"] += 20
                    progress["moves"].append("Solved secret room puzzle and obtained Enchanted Scroll")
                    break
                else:
                    print("That is not correct. Try again.")
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "ignore":
            print("You decide to ignore the artifacts and return to the hall.")
            progress["moves"].append("Ignored secret room puzzle")
            break
        else:
            print("Invalid choice. Please choose 'inspect' or 'ignore'.")
    
    # After the secret room, the player is directed to the treasure room.
    progress["current_room"] = "treasure_room"
    return progress

def treasure_room(progress):
    """
    The treasure room is the final room, filled with riches.
    The player may choose to take some treasure, affecting their score and inventory.
    """
    print("\n[Treasure Room]")
    print("You enter a room filled with glittering treasure—gold, jewels, and mystical relics lie before you!")
    progress["moves"].append("Entered treasure room and collected treasure")
    
    take = input("Do you want to take some treasure? (yes/no): ").strip().lower()
    if take == "yes":
        progress["inventory"].append("Bag of Gold")
        progress["score"] += 30
        print("You take a bag of gold. Your wealth increases!")
    else:
        print("You decide not to take anything and simply admire the view.")
    
    progress["current_room"] = "end"
    return progress

def game_loop():
    """
    The main game loop that controls the flow of the adventure.
    """
    progress = load_progress()
    print("Welcome to the Enhanced Text Adventure Game!")
    
    while progress.get("current_room") != "end":
        room = progress.get("current_room")
        if room == "start":
            progress = start_room(progress)
        elif room == "puzzle_room":
            progress = puzzle_room(progress)
        elif room == "secret_room":
            progress = secret_room(progress)
        elif room == "treasure_room":
            progress = treasure_room(progress)
        else:
            print("You seem to be lost in the game world!")
            progress["moves"].append("Encountered an unknown room")
            progress["current_room"] = "end"
        
        save_progress(progress)
        
        # Optionally, allow the player to quit after each room.
        cont = input("Continue playing? (yes/no): ").strip().lower()
        if cont == "no":
            print("Exiting game and saving progress.")
            save_progress(progress)
            return
    
    print("\nGame Over. Final Progress:")
    print(json.dumps(progress, indent=4))

if __name__ == "__main__":
    game_loop()
