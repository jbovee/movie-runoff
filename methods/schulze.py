from .voting_method import VotingMethod


class SchulzeMethod(VotingMethod):
    """
    Implementation of the Schulze voting method, also known as the Beatpath method.

    This method determines winners by:
    1. Computing pairwise preferences between all candidates
    2. Finding the strongest paths between candidates using the Floyd-Warshall algorithm
    3. Ranking candidates based on their overall victory strength

    Attributes:
        n (int): Number of candidates/movies
        d (list): 2D matrix storing direct pairwise preferences
        p (list): 2D matrix storing strongest paths between candidates
    """

    def __init__(self, movies, ballots, **kwargs):
        """
        Initialize the Schulze method calculator.

        Args:
            movies (list): List of movie candidates
            ballots (list): List of Ballot objects containing voter preferences
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(movies, ballots, **kwargs)
        self.n = len(movies)
        self.d = [[0 for i in range(self.n)] for j in range(self.n)]
        self.p = [[0 for i in range(self.n)] for j in range(self.n)]

    def score_pairwise(self):
        """
        Calculate direct pairwise preferences between all candidates.

        For each pair of candidates (i,j), counts how many voters preferred i over j
        by comparing their rankings. Results are stored in the d matrix.
        """
        # For each pair of candidates, count how many voters prefer i over j
        for ballot in self.ballots:
            for i in range(self.n):
                for j in range(self.n):
                    if i != j and ballot.votes[i] != -1 and ballot.votes[j] != -1:
                        if ballot.votes[i] < ballot.votes[j]:
                            self.d[i][j] += 1

    def compute_paths(self):
        """
        Calculate the strongest paths between all pairs of candidates.

        Uses the Floyd-Warshall algorithm to find the strongest path between each
        pair of candidates. A path's strength is equal to the minimum pairwise
        victory along that path. Results are stored in the p matrix.
        """
        # Find strongest paths between each pair using Floyd-Warshall algorithm
        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    if self.d[i][j] > self.d[j][i]:
                        self.p[i][j] = self.d[i][j]
                    else:
                        self.p[i][j] = 0

        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    for k in range(self.n):
                        if i != k and j != k:
                            self.p[j][k] = max(
                                self.p[j][k], min(self.p[j][i], self.p[i][k])
                            )

    def get_strength_grid(self):
        """
        Generate a formatted string showing pairwise preference counts.

        The grid shows how many voters preferred candidate i over candidate j
        for each pair. Values are color-coded:
        - Green: More voters preferred row candidate over column candidate
        - Red: More voters preferred column candidate over row candidate

        Returns:
            str: Formatted string containing the colored strength grid
        """
        # ANSI color codes
        GREEN = "\033[92m"
        RED = "\033[91m"
        RESET = "\033[0m"

        lines = []
        lines.append("Pairwise Strength Grid:")

        # Header row with movie letters
        header = " " * 3
        for i in range(self.n):
            header += f"{chr(65 + i):>3}"
        lines.append(header)
        lines.append("   " + "-" * self.n * 3)

        # Each row with strength scores
        for i in range(self.n):
            row = f"{chr(65 + i)} |"
            for j in range(self.n):
                if i == j:
                    row += f"{'-':>3}"
                else:
                    if self.d[i][j] > self.d[j][i]:
                        color = GREEN
                    elif self.d[i][j] < self.d[j][i]:
                        color = RED
                    else:
                        color = ""
                    row += f"{color}{self.d[i][j]:3}{RESET}"
            row += f" | {chr(65 + i)}: {self.movies[i]}"
            lines.append(row)

        return "\n".join(lines) + "\n"

    def get_preference_order(self, winners, losers):
        """
        Generate a formatted string showing the final preference ordering.

        Candidates are represented by letters (A, B, C, etc.). Tied candidates
        are grouped in blue-colored brackets.

        Args:
            winners (list): List of winning candidates (may include nested lists for ties)
            losers (list): List of losing candidates in preference order

        Returns:
            str: Formatted string showing the complete preference order
        """
        # ANSI color codes
        BLUE = "\033[94m"
        RESET = "\033[0m"

        result = "Preference Order: "

        for winner in winners:
            if isinstance(winner, list):
                # Handle tied winners
                tied_letters = [chr(65 + self.movies.index(movie)) for movie in winner]
                result += f"{BLUE}[{''.join(sorted(tied_letters))}]{RESET}"
            else:
                # Single winner
                result += chr(65 + self.movies.index(winner))

        # Process losers
        for loser in losers:
            result += chr(65 + self.movies.index(loser))

        return result + "\n"

    def process_ballots(self):
        """
        Process all ballots to determine winners and losers using the Schulze method.

        The method:
        1. Calculates pairwise preferences
        2. Computes strongest paths
        3. Determines victory strength for each candidate
        4. Groups candidates by score to handle ties
        5. Separates winners and losers based on victory strength

        Returns:
            tuple: (winners, losers) where:
                - winners: List of winning candidates (or nested lists for ties)
                - losers: List of remaining candidates in order of preference
        """
        self.score_pairwise()
        self.compute_paths()

        # Calculate strength of victory for each candidate
        strength_scores = []
        for i in range(self.n):
            victory_margin_sum = 0
            for j in range(self.n):
                if i != j:
                    # Add the margin of victory (can be negative if lost)
                    margin = self.p[i][j] - self.p[j][i]
                    victory_margin_sum += margin
            strength_scores.append((victory_margin_sum, i))

        # Sort by victory margin sum (highest to lowest)
        strength_scores.sort(reverse=True)

        # Group candidates by score to find ties
        score_groups = {}
        for score, idx in strength_scores:
            if score not in score_groups:
                score_groups[score] = []
            score_groups[score].append(self.movies[idx])

        # Build winners list with ties represented as nested lists
        winners = []
        remaining_winners_needed = self.num_winners
        scores = sorted(score_groups.keys(), reverse=True)

        for score in scores:
            candidates = score_groups[score]
            if len(candidates) == 1 and remaining_winners_needed > 0:
                winners.append(candidates[0])
                remaining_winners_needed -= 1
            elif len(candidates) > 1:
                self.tie = True
                if remaining_winners_needed > 0:
                    winners.append(candidates)
                    remaining_winners_needed = 0
                else:
                    break
            if remaining_winners_needed == 0:
                break

        # Build losers list from remaining candidates
        losers = []
        winners_flat = []
        for winner in winners:
            if isinstance(winner, list):
                winners_flat.extend(winner)  # Add all tied candidates
            else:
                winners_flat.append(winner)

        for score in scores:
            candidates = score_groups[score]
            for candidate in candidates:
                if candidate not in winners_flat:
                    losers.append(candidate)

        return winners, losers

    def get_debug(self, winners, losers):
        """
        Generate debug information combining the strength grid and preference order.

        Args:
            winners (list): List of winning candidates
            losers (list): List of losing candidates

        Returns:
            str: Combined debug information as a formatted string
        """
        return "\n".join(
            [self.get_strength_grid(), self.get_preference_order(winners, losers)]
        )
