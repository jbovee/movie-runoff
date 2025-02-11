import os
import argparse
from methods import VotingMethodFactory
from domain import Ballot, acquire_file, parse_file


class Election:
    def __init__(self, filepath, **kwargs):
        self.file_contents = parse_file(filepath)
        self.movies, self.ballots = Ballot.load_from_file_contents(self.file_contents)
        self.quiet = kwargs.get("quiet", False)
        self.tie = False
        self.method = kwargs.get("method", "schulze")
        self.num_winners = kwargs.get("num_winners", 1)
        self.show_losers = kwargs.get("show_losers", True)
        self.winners = []
        self.losers = []
        print(f"~~~~~ Using {self.method.title()} Method ~~~~~")

    def calculate(self):
        voting_method = VotingMethodFactory.create_method(
            self.method, self.movies.copy(), self.ballots, num_winners=self.num_winners
        )
        self.winners, self.losers = voting_method.process_ballots()
        self.tie = voting_method.tie

        # Print results
        winner_number = 1
        for i, winner in enumerate(self.winners):
            if isinstance(winner, list):
                for w in winner:
                    print(f'{"Winner: " if i == 0 else f"*#{i+1}: ":>8}{w}')
                    winner_number += 1
            else:
                print(f'{"Winner: " if i == 0 else f"#{winner_number}: ":>8}{winner}')
                winner_number += 1
        if self.tie:
            print("\n* indicates a tie")
        if self.show_losers and self.losers:
            print("\nEliminated:")
            for loser in self.losers:
                if isinstance(loser, list):
                    print(f'{" ":>8}{", ".join(loser)}* (tied)')
                else:
                    print(f'{" ":>8}{loser}')
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Perform vote calculations for movie night"
    )
    parser.add_argument(
        "-q",
        "--quiet",
        help="ignore all print statements except for final results",
        action="store_true",
    )
    parser.add_argument(
        "-l",
        "--show_losers",
        help="show eliminated movies in order after winners",
        action="store_true",
    )
    parser.add_argument(
        "-r",
        "--reorder_votes",
        help="after a movie is removed, reorder the ballot votes to the lowest possible numbers (i.e. [1,2,4,5,7] -> [1,2,3,4,5])",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--select",
        help="select a file instead of using the most recent expected filename",
        action="store_true",
    )
    parser.add_argument(
        "-m",
        "--method",
        help="voting method to use",
        choices=["instant", "instant-reorder", "schulze"],
        default="schulze",
    )
    parser.add_argument(
        "-n", "--num_winners", help="number of winners to select", type=int, default=1
    )
    args = parser.parse_args()

    cwd = os.getcwd()
    ballots_dir = os.path.join(cwd,"ballots")
    if not os.path.exists(ballots_dir) and not args.select:
        print(f"{ballots_dir} doesn't exist. Creating now")
    filepath = acquire_file(args.select, "Runoff Votes", path=ballots_dir)

    election = Election(filepath, **vars(args))
    election.calculate()


if __name__ == "__main__":
    main()
