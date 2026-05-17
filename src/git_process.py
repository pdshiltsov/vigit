# Copyright (C) 2025 vigit
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.

from dataclasses import dataclass
import subprocess


@dataclass
class Commit:
    _hash: str
    _parents: list[str]
    _author: str
    _date: str
    _msg: str
    

def get_commits():
    result = subprocess.run(
        [
            "git",
            "log",
            "--all",
            "--pretty=format:%H|%P|%an|%ad|%s"
        ],
        capture_output=True,
        text=True
    )

    commits = []

    for line in result.stdout.splitlines():
        commit_hash, parents, author, date, message = line.split("|", 4)

        commits.append(Commit(
            commit_hash,
            parents.split(),
            author,
            date,
            message,
    
        ))

    return commits[::-1]


if __name__ == "__main__":
    commits = get_commits()
    for c in commits:
        print("HASH:", c._hash)
        print("PARENTS:", c._parents)
        print("MESSAGE:", c._msg)
        print()
