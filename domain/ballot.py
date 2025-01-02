import re


class Ballot:
    total_ballots = 0

    def __init__(self, votes, **kwargs):
        self.id = Ballot.total_ballots
        Ballot.total_ballots += 1
        self.votes = votes

    def __repr__(self) -> str:
        return f"Ballot{self.id}[{self.votes}]"

    @classmethod
    def load_from_file_contents(cls, file_contents, **kwargs):
        """Load movies and ballots from file contents."""
        movies = [
            re.search(r"\[(.+)\]", movie).group(1) for movie in file_contents[0][1:]
        ]

        ballots = []
        for ballot in list(file_contents[1:]):
            ballots.append(
                cls([int(val) if val != "" else -1 for val in ballot[1:]], **kwargs)
            )

        return movies, ballots
