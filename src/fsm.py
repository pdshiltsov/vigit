class LSI: # Linear state iterator
    def __init__(self, state_sequence: list[str]) -> None:
        self.state_sequence = state_sequence
        self._pos = 0

    def previous(self) -> None:
        if self._pos - 1 >= 0:
            self._pos -= 1

    def following(self) -> None:
        if self._pos + 1 < len(self.state_sequence):
            self._pos += 1

    @property
    def state(self) -> str:
        return self.state_sequence[self._pos]
        
class FSM:
    pass
