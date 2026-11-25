#!/usr/bin/env python3
"""Keep the Korean fork current and install it as the agent-home copy.

    python3 tools/sync.py check     fetch upstream, list unmerged commits and local changes
    python3 tools/sync.py update    merge upstream (stops before committing), then install
    python3 tools/sync.py install   copy the tracked files of `ko` into agent-home

No commits or pushes. Upstream merges stop before committing; conflicts and
uncommitted changes stop updates before the installed copy is replaced.
tools/ stays out of the installed skill. The Korean patch is `git diff upstream/main...ko`.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

NAME = "image-prompt-reverse"
BRANCH = "ko"
UPSTREAM = "upstream/main"
SOURCE = Path(__file__).resolve().parents[1]
SKILLS = Path.home() / "Work" / "agent-home" / "skills"


def git(*args: str, raw: bool = False) -> str:
    result = subprocess.run(["git", "-C", str(SOURCE), *args], check=True, text=True, stdout=subprocess.PIPE)
    return result.stdout if raw else result.stdout.strip()


def require_branch() -> None:
    if git("branch", "--show-current") != BRANCH:
        raise RuntimeError(f"{BRANCH} 브랜치에서 실행한다: {SOURCE}")
    git("rev-parse", "--verify", UPSTREAM)
    if git("ls-files", "-u"):
        raise RuntimeError("충돌을 먼저 해결한다. 설치본은 유지한다.")


def merge_head() -> Path:
    path = Path(git("rev-parse", "--git-path", "MERGE_HEAD"))
    return path if path.is_absolute() else SOURCE / path


def upstream_base() -> str:
    if merge_head().exists():
        heads = merge_head().read_text().splitlines()
        if len(heads) != 1:
            raise RuntimeError("여러 브랜치를 합치는 중에는 설치하지 않는다.")
        return heads[0]
    return git("merge-base", "HEAD", UPSTREAM)


def skill_files() -> list[Path]:
    names = filter(None, git("ls-files", "-z", raw=True).split("\0"))
    return [Path(name) for name in names if not name.startswith("tools/")]


def install() -> None:
    require_branch()
    base = upstream_base()
    target = SKILLS / NAME
    if target.is_symlink() or (target.exists() and not target.is_dir()):
        raise RuntimeError(f"설치 경로는 디렉터리여야 한다: {target}")
    with tempfile.TemporaryDirectory(prefix=f".{NAME}-", dir=SKILLS) as temporary:
        candidate = Path(temporary) / "candidate"
        for relative in skill_files():
            path = SOURCE / relative
            if relative.is_absolute() or ".." in relative.parts or path.is_symlink() or not path.is_file():
                raise RuntimeError(f"일반 파일만 설치한다: {relative}")
            destination = candidate / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
        if not (candidate / "SKILL.md").is_file() or not (candidate / "LICENSE").is_file():
            raise RuntimeError("SKILL.md 또는 LICENSE 가 없다. 설치본은 유지한다.")
        previous = Path(temporary) / "previous"
        if target.exists():
            target.rename(previous)
        try:
            candidate.rename(target)
        except OSError:
            if previous.exists():
                previous.rename(target)
            raise
    print(f"설치본 갱신: {target} (상류 {base[:7]}). agent-home 에서 검토·커밋한다 — 커밋 메시지에 상류 {base[:7]} 를 적는다.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", choices=("check", "update", "install"))
    action = parser.parse_args().action
    if action != "install":
        git("fetch", "upstream")  # 새 clone 엔 upstream/main 이 아직 없다 — 확인보다 먼저
    require_branch()
    if action == "install":
        install()
        return
    newer = git("log", "--oneline", f"HEAD..{UPSTREAM}")
    print(newer or "미반영 상류 커밋 없음")
    if action == "check":
        print(git("status", "--short") or "로컬 변경 없음")
        return
    if newer:
        if git("status", "--porcelain"):
            raise RuntimeError("미커밋 변경이 있다. 먼저 검토·커밋한 뒤 update 를 다시 실행한다.")
        if merge_head().exists():
            raise RuntimeError("진행 중인 병합을 먼저 마친다.")
        git("merge", "--no-commit", "--no-ff", UPSTREAM)
    install()
    if newer:
        print("상류 병합은 커밋 전에 멈췄다. diff 를 검토한 뒤 직접 커밋한다. 푸시는 실행하지 않는다.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, OSError) as error:
        raise SystemExit(str(error)) from error
