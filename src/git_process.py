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

import subprocess
from dataclasses import dataclass, field


FIELD_SEP = "\x1f"  # Unit Separator
COMMIT_SEP = "\x1e"  # Record Separator

FORMAT = FIELD_SEP.join([
    "%H",   # full hash
    "%h",   # short hash
    "%an",  # author name
    "%ae",  # author email
    "%at",  # author timestamp (unix)
    "%cn",  # committer name
    "%ce",  # committer email
    "%ct",  # committer timestamp (unix)
    "%P",   # parent hashes (space-separated)
    "%D",   # refs (HEAD, branches, tags)
    "%s",   # subject
    "%b",   # body
]) + COMMIT_SEP


@dataclass
class Commit:
    hash: str
    short_hash: str
    author_name: str
    author_email: str
    author_ts: int
    committer_name: str
    committer_email: str
    committer_ts: int
    parents: list[str]     
    refs: list[str]      
    subject: str
    body: str

    @property
    def is_merge(self) -> bool:
        return len(self.parents) > 1

    @property
    def is_root(self) -> bool:
        return len(self.parents) == 0


def get_commits(repo_path: str = ".", max_count: int = 200) -> list[Commit]:
    result = subprocess.run(
        [
            "git", "-C", repo_path,
            "log",
            f"--pretty=format:{FORMAT}",
            f"--max-count={max_count}",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    commits = []
    
    for raw in result.stdout.split(COMMIT_SEP)[::-1]:
        parts = raw.split(FIELD_SEP)
        
        if not raw.strip():
            continue
        
        (
            hash_, short_hash, author_name, author_email, author_ts,
            committer_name, committer_email, committer_ts,
            parents_raw, refs_raw, subject, body,
        ) = parts[:12]

        pre_parents = parents_raw.split()
        parents = []
        for commit in commits:
            if commit.hash in pre_parents:
                parents.append(commit)
        
        commits.append(Commit(
            hash=hash_.strip(),
            short_hash=short_hash,
            author_name=author_name,
            author_email=author_email,
            author_ts=int(author_ts or 0),
            committer_name=committer_name,
            committer_email=committer_email,
            committer_ts=int(committer_ts or 0),
            parents=parents,
            refs=[r.strip() for r in refs_raw.split(",") if r.strip()],
            subject=subject,
            body=body.strip(),
        ))

    return commits

if __name__ == "__main__":
    commits = get_commits()
    for c in commits:
        print("HASH:", c.hash)
        print("PARENTS:", c.parents)
        print("SUBJECT:", c.subject)
        print("BODY:", c.body)
        print()
