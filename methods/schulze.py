from methods.method_factory import VotingMethod


class SchulzeMethod(VotingMethod):
    def __init__(self, movies, ballots, **kwargs):
        super().__init__(movies, ballots, **kwargs)
        self.n = len(movies)
        self.d = [[0 for i in range(self.n)] for j in range(self.n)]
        self.p = [[0 for i in range(self.n)] for j in range(self.n)]

    def score_pairwise(self):
        # For each pair of candidates, count how many voters prefer i over j
        for ballot in self.ballots:
            for i in range(self.n):
                for j in range(self.n):
                    if i != j and ballot.votes[i] != -1 and ballot.votes[j] != -1:
                        if ballot.votes[i] < ballot.votes[j]:
                            self.d[i][j] += 1

    def compute_paths(self):
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

    def process_ballots(self):
        self.score_pairwise()
        self.compute_paths()

        # Calculate strength of victory for each candidate
        strength_scores = []
        for i in range(self.n):
            wins = 0
            for j in range(self.n):
                if i != j and self.p[i][j] > self.p[j][i]:
                    wins += 1
            strength_scores.append((wins, i))

        # Sort by number of wins (highest to lowest)
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
        for score in scores:
            candidates = score_groups[score]
            for candidate in candidates:
                if candidate not in [
                    c if isinstance(c, str) else c[0] for c in winners
                ]:
                    losers.append(candidate)

        return winners, losers
