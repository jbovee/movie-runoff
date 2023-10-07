import re
import sys
import argparse
from random import randint
from gform_csvzip import acquire_file, parse_file

class Ballot:
    total_ballots = 0

    def __init__(self, votes):
        self.id = Ballot.total_ballots
        Ballot.total_ballots += 1
        self.votes = votes

    def __repr__(self) -> str:
        return f'Ballot{self.id}[{self.votes}]'
    
class Runoff:
    def __init__(self, filepath, quiet):
        self.lowest = 0
        self.movies = []
        self.ballots = []
        self.file_contents = parse_file(filepath)
        self.load_ballots()
        self.maxVote = len(self.movies)
        self.quiet = quiet
        self.tie = False
    
    def load_ballots(self):
        self.movies = [re.search(r'\[(.+)\]', movie).group(1) for movie in self.file_contents[0][1:]]
        for ballot in list(self.file_contents[1:]):
            self.ballots.append(Ballot([int(val) if val != '' else -1 for val in ballot[1:]]))
    
    def count_num_votes_for_movie(self,voteNum,movieIndex):
        return sum([1 for ballot in self.ballots if ballot.votes[movieIndex] == voteNum])

    def drop_movies_with_no_first_votes(self,reorder):
        s = 0
        e = len(self.movies)
        while(s < e):
            if self.count_num_votes_for_movie(1,s) == 0:
                if not self.quiet:
                    print(f'{self.movies[s]} dropped.')
                self.shift_first_votes(s)
                if reorder:
                    self.maxVote -= 1
                    self.reorder_ballots()
                e -= 1
            else:
                s += 1
    
    def shift_first_votes(self,movieIndex):
        for ballot in self.ballots:
            if ballot.votes[movieIndex] == 1:
                nextHighestVote = get_next_highest_in_array(1,ballot.votes)
                indToSwap = ballot.votes.index(nextHighestVote)
                ballot.votes[indToSwap] = 1
            ballot.votes.pop(movieIndex)
        self.movies.pop(movieIndex)
    
    def get_movie_indices_with_lowest_count_of_vote(self,indicesToCheck,voteNum):
        indexCounts = {idx:0 for idx in indicesToCheck}
        for ind in indicesToCheck:
            for ballot in self.ballots:
                if ballot.votes[ind] == voteNum:
                    indexCounts[ind] += 1
        lowest = min(indexCounts.values())
        return [key for key,val in indexCounts.items() if val == lowest]
    
    def print_movies(self):
        print([movie for movie in self.movies])
    
    def print_ballots(self):
        for ballot in self.ballots:
            print(ballot.votes)
    
    def reorder_ballots(self):
        for ballot in self.ballots:
            orderedVotes = sorted(ballot.votes)
            for i,v in enumerate(orderedVotes):
                idxToSwap = ballot.votes.index(v)
                ballot.votes[idxToSwap] = i + 1

    
    def runoff(self,reorder):
        if not self.quiet:
            self.print_movies()
            self.print_ballots()
            print('Dropping movies with no 1 votes')
        self.drop_movies_with_no_first_votes(reorder)
        while(len(self.movies) > 1):
            if not self.quiet:
                print()
                self.print_movies()
                self.print_ballots()
            indicesToCheck = list(range(len(self.movies)))
            for vote in range(1,self.maxVote+1):
                indicesToCheck = self.get_movie_indices_with_lowest_count_of_vote(indicesToCheck,vote)
                if len(indicesToCheck) == 1:
                    if not self.quiet:
                        print(f'Dropping {self.movies[indicesToCheck[0]]}; least {vote} votes')
                    self.shift_first_votes(indicesToCheck[0])
                    if reorder:
                        self.maxVote -= 1
                        self.reorder_ballots()
                    break
                else:
                    if not self.quiet:
                        print(f'Tie for least {vote} votes; {", ".join([self.movies[idx] for idx in indicesToCheck])}')
                if vote == self.maxVote:
                    self.tie = True
                    if not self.quiet:
                        print(f'Full ballot tie; {", ".join([self.movies[idx] for idx in indicesToCheck])}')
                    randIndex = randint(0,len(indicesToCheck)-1)
                    if not self.quiet:
                        print(f'{self.movies[indicesToCheck[randIndex]]} has been randomly chosen to drop')
                    self.shift_first_votes(indicesToCheck[randIndex])
                    if reorder:
                        self.maxVote -= 1
                        self.reorder_ballots()
        print(f'Winner is: {self.movies[0]}{"*" if self.tie else ""}\n')

def main():
    parser = argparse.ArgumentParser(description='Perform runoff vote calculations for movie night')
    parser.add_argument('-q','--quiet',help='ignore all print statements except the one for the winner',action='store_true')
    parser.add_argument('-r','--reorder_votes',help='after a movie is removed, reorder the ballot votes to the lowest possible numbers (i.e. [1,2,4,5,7] -> [1,2,3,4,5])',action='store_true')
    parser.add_argument('-s','--select',help='select a file instead of using the most recent expected filename',action='store_true')
    args = parser.parse_args()

    filepath = acquire_file(args.select, 'Runoff Votes', path='exports/')
    print(f'~~~~~ All Ballots ~~~~~')
    allRunoff = Runoff(filepath,args.quiet)
    allRunoff.runoff(False)

    print(f'~~~~~ All Ballots Reordered ~~~~~')
    allRunoffReorder = Runoff(filepath,args.quiet)
    allRunoffReorder.runoff(True)

def get_next_highest_in_array(start,arr):
    nextHighest = sys.maxsize
    for val in arr:
        if val < nextHighest and val > start:
            nextHighest = val
    return nextHighest

if __name__ == "__main__":
    main()