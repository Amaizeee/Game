import random

def play_random_number_game():
    """Play an interactive random number guessing game."""
    print("Welcome to the Random Number Guessing Game!")
    print("I'm thinking of a number between 1 and 100.")
    print("Try to guess it. Type 'quit' to exit.\n")

    target = random.randint(1, 100)
    attempts = 0

    while True:
        user_input = input("Enter your guess: ").strip()

        if user_input.lower() == "quit":
            print("Thanks for playing! Goodbye.")
            break

        if not user_input.isdigit():
            print("Please enter a valid number between 1 and 100, or 'quit' to exit.")
            continue

        guess = int(user_input)
        if guess < 1 or guess > 100:
            print("Your guess is out of range. Try a number between 1 and 100.")
            continue

        attempts += 1

        if guess < target:
            print("Too low! Try again.")
        elif guess > target:
            print("Too high! Try again.")
        else:
            print(f"Congratulations! You guessed the number {target} in {attempts} attempts.")
            play_again = input("Would you like to play again? (yes/no): ").strip().lower()
            if play_again in {"yes", "y"}:
                target = random.randint(1, 100)
                attempts = 0
                print("\nGreat! I'm thinking of a new number between 1 and 100.\n")
                continue

            print("Thanks for playing! Goodbye.")
            break

if __name__ == "__main__":
    play_random_number_game()
