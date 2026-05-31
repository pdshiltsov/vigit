# vigit - Minimal TUI application for working with Git directly from the terminal.
# Copyright (C) 2026 vigit Pavel Shiltsov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

class LSI: # Linear state iterator
    def __init__(self, state_sequence: list[str]) -> None:
        self.state_sequence = state_sequence
        self._pos = 0
        self._info = {
            key: {"cursor": 0, "info": None} for key in state_sequence
        }
        
    def previous(self) -> None:
        if self._pos - 1 >= 0:
            self._pos -= 1

    def following(self) -> None:
        if self._pos + 1 < len(self.state_sequence):
            self._pos += 1

    @property
    def status(self) -> str:
        return self.state_sequence[self._pos]

    @property
    def info(self) -> dict:
        return self._info[self.state_sequence[self._pos]]

    
class FSM: 
    def __init__(self, states: dict[str, LSI]) -> None:
        self.states = states
        self._pos = list(states.keys())[0]
        
    @property
    def state(self) -> LSI:
        return self.states[self.pos]

    @property
    def pos(self) -> str:
        return self._pos

    def change_state(self, new_state: str) -> None:
        if new_state in self.states.keys():
            self._pos = new_state
        else:
            raise ValueError(f"Incorrect state, got: {new_state} instead of {self.states}")

    
