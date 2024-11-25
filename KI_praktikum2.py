import random
from collections import Counter


class Player:
    def __init__(self, name, strategy="random"):
        self.name = name
        self.strategy = strategy
        self.is_protected = False
        self.charge = 0
        self.is_alive = True

    def reset(self):
        self.is_protected = False  # Schutz wird jede Runde zurückgesetzt

    def reset_game(self):
        self.is_protected = False
        self.charge = 0
        self.is_alive = True

    def __repr__(self):
        return f"{self.name} (Strategy: {self.strategy}, Charge: {self.charge}, Alive: {self.is_alive})"


class Game:
    def __init__(self, num_players=3, strategies=None):
        if strategies is None:
            strategies = ["random"]
        self.players = [Player(f"Player {i + 1}", strategy=strategies[i % len(strategies)]) for i in range(num_players)]
        self.rounds = 0

    def reset_game(self):
        for player in self.players:
            player.reset_game()
        self.rounds = 0

    def determine_action(self, player):
        if not player.is_alive:
            return None, None  # Keine Aktion, wenn tot


        elif player.strategy == "aggressive":
            if player.charge >= 3:
                action = "rocket"
            elif player.charge >= 2:
                action = "shoot"
            else:
                action = "charge"
        elif player.strategy == "defensive":
            if player.is_protected:
                action = "charge"
            elif random.random() < 0.7:
                action = "protect"
            else:
                action = "charge"
        else:
            action = "charge"  # Standardaktion, wenn keine Strategie passt

        # Wähle ein Ziel, falls die Aktion ein Angriff ist
        if action in ["shoot", "rocket"]:
            target = random.choice([p for p in self.players if p.is_alive and p != player])
        else:
            target = None

        return action, target

    def execute_actions(self, actions):
        # Aktionen sammeln
        rockets = []  # Spieler, die Raketen abschießen
        shots = []    # Spieler, die schießen
        protects = set()  # Spieler, die sich schützen
        chargers = set()  # Spieler, die laden

        # Aktionen auswerten
        for player, (action, target) in actions.items():
            if action == "protect":
                protects.add(player)
            elif action == "charge":
                chargers.add(player)
            elif action == "shoot" and player.charge >= 2:
                shots.append((player, target))
                player.charge -= 2
            elif action == "rocket" and player.charge >= 3:
                rockets.append((player, target))
                player.charge -= 3

        # Raketen booooom   (gehen durch Schutz durch)
        for rocket_shooter, target in rockets:
            if target.is_alive:
                target.is_alive = False

        # Schüsse  (Schutz verhindert den Tod)
        for shooter, target in shots:
            if target.is_alive and target not in protects:
                target.is_alive = False

        # Ladeaktionen
        for charger in chargers:
            charger.charge += 1

        # Schutz wush
        for protector in protects:
            protector.is_protected = True

    def is_game_over(self):
        alive_players = [p for p in self.players if p.is_alive]
        return len(alive_players) <= 1

    def run(self):
        self.rounds = 0
        while not self.is_game_over() and self.rounds < 1000:  # Begrenzung auf 1000 Runden
            self.rounds += 1

            # gather actions togetherrr
            actions = {player: self.determine_action(player) for player in self.players if player.is_alive}


            self.execute_actions(actions)

            # Schutz zurücksetzen
            for player in self.players:
                player.reset()

        # bestimmung von gewinner, nur eine person kann gewinnen.
        alive_players = [p.name for p in self.players if p.is_alive]
        return alive_players[0] if alive_players else None


def simulate_games(num_games, num_players=3, strategies=None):


    game = Game(num_players=num_players, strategies=strategies)
    results = Counter()
    total_rounds = 0

    for iteration in range(num_games):
        winner = game.run()
        if winner:
            results[winner] += 1
        total_rounds += game.rounds
        game.reset_game()

    avg_rounds = total_rounds / num_games
    print("\n-Statistik -")
    print("Gewinne pro Spieler:")
    for player in game.players:
        print(f"{player.name}: {results[player.name]} Siege (Strategie: {player.strategy})")
    print(f"Durchschnittliche Rundenanzahl:{avg_rounds}")


if __name__ == "__main__":
    strategies = ["aggressive", "defensive"]
    simulate_games(num_games=1000, num_players=3, strategies=strategies)
