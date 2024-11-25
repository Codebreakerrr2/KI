import random


class Player:
    def __init__(self, name):
        self.name = name
        self.is_protected = False
        self.charge = 0
        self.is_alive = True
        self.last_action = None

    def reset(self):
        self.is_protected = False

    def reset_game(self):
        self.is_protected = False
        self.charge = 0
        self.is_alive = True
        self.last_action = None

    def __repr__(self):
        return f"{self.name} (Charge: {self.charge}, Alive: {self.is_alive})"


class Game:
    def __init__(self, user, bot):
        self.user = user
        self.bot = bot
        self.rounds = 0

    def reset_game(self):
        self.user.reset_game()
        self.bot.reset_game()
        self.rounds = 0

    def is_game_over(self):
        """Überprüft, ob das Spiel beendet ist."""
        return not (self.user.is_alive and self.bot.is_alive)

    def generate_actions(self, player):
        """Ermittelt die möglichen Aktionen basierend auf Ladung."""
        actions = [1, 2]  # Schutz und Laden
        if player.charge >= 1:  # Schießen ab 1 Ladung verfügbar
            actions.append(3)
        if player.charge >= 3:  # Rakete benötigt 3 Ladungen
            actions.append(4)
        return actions

    def process_round(self, user_action, bot_action):
        """Verarbeitet eine Runde basierend auf den Aktionen der Spieler."""
        # Beide Aktionen ausführen
        self.execute_action(self.user, user_action)
        self.execute_action(self.bot, bot_action)

        # Prüfen, was passiert
        if user_action == 3 and self.bot.is_alive and not self.bot.is_protected:
            self.bot.is_alive = False
        if bot_action == 3 and self.user.is_alive and not self.user.is_protected:
            self.user.is_alive = False

        if user_action == 4 and self.bot.is_alive:  # Rakete ignoriert Schutz
            self.bot.is_alive = False
        if bot_action == 4 and self.user.is_alive:  # Rakete ignoriert Schutz
            self.user.is_alive = False

        # Nach jeder Runde: Schutzstatus entfernen
        self.user.reset()
        self.bot.reset()

    def execute_action(self, player, action):
        """Führt eine Aktion aus."""
        if action == 1:  # Schutz
            player.is_protected = True
        elif action == 2:  # Laden
            player.charge += 1
        elif action == 3:  # Schießen
            player.charge = max(0, player.charge - 1)
        elif action == 4:  # Rakete
            player.charge -= 3


class MCGS:
    def __init__(self, game, num_simulations=1000):
        self.game = game
        self.num_simulations = num_simulations

    def select_action(self, bot, user):
        """Wählt die beste Aktion für den Bot mit MCGS."""
        actions = self.game.generate_actions(bot)
        action_scores = {action: 0 for action in actions}

        for action in actions:
            for _ in range(self.num_simulations):
                bot_copy = Player("Bot")
                user_copy = Player("Du")
                bot_copy.charge = bot.charge
                user_copy.charge = user.charge

                # Simuliere die Aktion
                self.simulate(bot_copy, user_copy, action)

                # Bewertung der Aktion
                if bot_copy.is_alive and not user_copy.is_alive:
                    action_scores[action] += 1  # Bot gewinnt
                elif not bot_copy.is_alive and user_copy.is_alive:
                    action_scores[action] -= 1  # Bot verliert

        # Wähle die Aktion mit dem höchsten Wert
        max_score = max(action_scores.values())
        best_actions = [action for action, score in action_scores.items() if score == max_score]
        return random.choice(best_actions)  # Zufällige Wahl bei Gleichstand

    def simulate(self, bot, user, action):
        """Simuliert eine Runde mit einer bestimmten Aktion."""
        target = user if action in [3, 4] else None
        self.game.execute_action(bot, action)
        if user.is_alive:
            possible_user_actions = self.game.generate_actions(user)
            user_action = random.choice(possible_user_actions)
            target = bot if user_action in [3, 4] else None
            self.game.execute_action(user, user_action)


def action_to_string(action):
    """Konvertiert eine Aktionsnummer in eine lesbare Form."""
    return {
        1: "Schutz",
        2: "Laden",
        3: "Schießen",
        4: "Rakete"
    }[action]


def play_game():
    # Initialisiere Spieler und Spiel
    user = Player("Du")
    bot = Player("Bot")
    game = Game(user, bot)
    mcgs = MCGS(game, num_simulations=1000)

    print("Willkommen zum Spiel! Kämpfe gegen den Bot.")
    print("Kurzanleitung:")
    print("1 = Schutz (verhindert Schießen, verliert aber bei Rakete)")
    print("2 = Laden (erhöht Ladung, wird bei Schießen eliminiert)")
    print("3 = Schießen (benötigt 1 Ladung, eliminiert Gegner, wenn ungeschützt)")
    print("4 = Rakete (benötigt 3 Ladungen, ignoriert Schutz)")

    while not game.is_game_over():
        game.rounds += 1
        print(f"\n--- Runde {game.rounds} ---")
        print(f"Dein Status: {user}")
        print(f"Bot-Status: {bot}")

        # Benutzerzug
        while True:
            try:
                user_action = int(input("Wähle deine Aktion (1-4): "))
                if user_action in game.generate_actions(user):
                    break
                else:
                    print("Ungültige Aktion. Versuche es erneut.")
            except ValueError:
                print("Bitte gib eine Zahl zwischen 1 und 4 ein.")

        bot_action = mcgs.select_action(bot, user)

        # Runde verarbeiten
        game.process_round(user_action, bot_action)

        print(f"\nDeine Aktion: {action_to_string(user_action)}")
        print(f"Bot-Aktion: {action_to_string(bot_action)}")

    # Gewinner anzeigen
    if user.is_alive:
        print("\nGlückwunsch! Du hast den Bot besiegt!")
    else:
        print("\nDer Bot hat dich besiegt!")


if __name__ == "__main__":
    play_game()
