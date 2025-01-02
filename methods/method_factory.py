from .schulze import SchulzeMethod
from .runoff import InstantRunoffMethod


class VotingMethodFactory:
    @staticmethod
    def create_method(method_name, movies, ballots, **kwargs):
        if method_name == "schulze":
            return SchulzeMethod(movies, ballots, **kwargs)
        elif method_name == "instant":
            return InstantRunoffMethod(movies, ballots, reorder=False, **kwargs)
        elif method_name == "instant-reorder":
            return InstantRunoffMethod(movies, ballots, reorder=True, **kwargs)
        else:
            raise ValueError(f"Unknown voting method: {method_name}")
