from abc import ABC, abstractmethod


class VotingMethod(ABC):
    def __init__(self, movies, ballots, **kwargs):
        self.movies = movies
        self.ballots = ballots
        self.tie = False
        self.num_winners = kwargs.get("num_winners", 1)

    @abstractmethod
    def process_ballots(self):
        """Calculate and return winners and losers.
        Returns (winners, losers) where:
            - winners is a list of length num_winners, where each element is either:
                - a single winner, or
                - a list of candidates tied for that position
            - losers is a list of remaining candidates in order
        """
        raise NotImplementedError("Subclass must implement process_ballots method")

    @abstractmethod
    def get_debug(self):
        """Returns human readable debug information to validate voting results.

        This method should return a string containing detailed information about the voting process
        and results that can be used to verify the correctness of the outcome. The information
        should include vote counts, elimination order, and any other method-specific details
        that would help validate the results.

        Returns:
            str: A formatted string containing the debug information
        """
        raise NotImplementedError("Subclass must implement get_debug method")
