import asyncio
import numpy as np

from poke_env.player.random_player import RandomPlayer, Player
from poke_env.player.utils import cross_evaluate
from poke_env.player_configuration import PlayerConfiguration
from poke_env.server_configuration import LocalhostServerConfiguration
from tabulate import tabulate


class RandomAgent(Player):
	def choose_move(self, battle):
		available_orders = []
		available_z_moves = set()

		if battle.can_z_move:
			available_z_moves.update(battle.active_pokemon.available_z_moves)
			if not available_z_moves:
				print(battle.active_pokemon.item)
				print(battle.active_pokemon.moves)

		for move in battle.available_moves:
			available_orders.append(self.create_order(move))
			if battle.can_mega_evolve:
				available_orders.append(self.create_order(move, mega=True))
			if battle.can_z_move and move in available_z_moves:
				available_orders.append(self.create_order(move, z_move=True))

		for pokemon in battle.available_switches:
			available_orders.append(self.create_order(pokemon))

		order = np.random.choice(available_orders)
		return order


async def main():
	# Configs for random agents, one from class defined above, one from library.
	player1 = PlayerConfiguration("Manual Random", None)
	player2 = PlayerConfiguration("Library Random", None)

	# Create the players from configs.
	players = [
		RandomAgent(
			player_configuration=player1,
			battle_format="gen7randombattle",
			server_configuration=LocalhostServerConfiguration,
		),
		RandomPlayer(
			player_configuration=player2,
			battle_format="gen7randombattle",
			server_configuration=LocalhostServerConfiguration,
		)
	]

	# Get results from 10 games
	cross_evaluation = await cross_evaluate(players, n_challenges=10)

	# Display results in a nice format
	table = [["-"] + [p.username for p in players]]
	for p_1, results in cross_evaluation.items():
		table.append([p_1] + [cross_evaluation[p_1][p_2] for p_2 in results])
	print(tabulate(table))


if __name__ == "__main__":
	asyncio.get_event_loop().run_until_complete(main())
