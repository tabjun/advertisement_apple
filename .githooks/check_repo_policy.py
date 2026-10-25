"""pre-commit 저장소 정책 검사 (apple 프로젝트용).

아직 활성화되지 않았다. 2026-10-15 personal_ai_project 모노레포에서 독립 저장소
(tabjun/advertisement_apple)로 분리되어, hookspath를 quantitative_trading과 나눠 쓰던
충돌 이유는 사라졌다. 쓰려면 .githooks/pre-commit에서 이 파일을 호출하고
`git config core.hooksPath .githooks`를 설정한다.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


# 독립 저장소라 이 폴더가 곧 루트다(예전 값 "apple/").
REPO_PREFIX = ""

# develop/main은 최종 결과물만 올라가는 브랜치라 아래 지침 파일들을 제외한다
# (AGENTS.md 2.2절). git merge는 이 규칙을 모르므로, 병합 커밋이든 일반
# 커밋이든 develop/main에서 이 파일들이 스테이징되면 여기서 차단한다.
GOVERNANCE_FILES = {
    f"{REPO_PREFIX}AGENTS.md",
    f"{REPO_PREFIX}CLAUDE.md",
    f"{REPO_PREFIX}chat_history.md",
    f"{REPO_PREFIX}history.md",
    f"{REPO_PREFIX}process.md",
    f"{REPO_PREFIX}state.md",
}
GOVERNANCE_EXCLUDED_BRANCHES = {"develop", "main"}


def run_git(args: list[str], cwd: Path) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True, encoding="utf-8").strip()


def repo_root() -> Path:
    return Path(run_git(["rev-parse", "--show-toplevel"], Path.cwd()))


def current_branch(root: Path) -> str:
    return run_git(["rev-parse", "--abbrev-ref", "HEAD"], root)


def staged_name_status(root: Path) -> list[tuple[str, str]]:
    output = run_git(["diff", "--cached", "--name-status", "--diff-filter=ACMRT"], root)
    rows = []
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            rows.append((parts[0], parts[-1]))
    return rows


def fail(message: str, details: list[str]) -> int:
    print(f"[repo-policy] {message}", file=sys.stderr)
    for detail in details:
        print(f"  - {detail}", file=sys.stderr)
    return 1


def main() -> int:
    root = repo_root()
    branch = current_branch(root)
    staged = staged_name_status(root)
    governance_errors: list[str] = []

    for status, path in staged:
        normalized = path.replace("\\", "/")
        if branch in GOVERNANCE_EXCLUDED_BRANCHES and normalized in GOVERNANCE_FILES and status != "D":
            governance_errors.append(
                f"{normalized}: '{branch}' 브랜치에는 작업 지침 파일을 커밋하지 않습니다(연구/분석 "
                "브랜치 전용, AGENTS.md 2.2절). git merge로 다시 들어왔다면 `git restore --staged "
                "--worktree -- <파일>`로 되돌리거나 `git rm --cached <파일>`로 제외한 뒤 다시 커밋하세요."
            )

    if governance_errors:
        return fail("지침 파일은 연구/분석 브랜치에만 존재해야 합니다", governance_errors)
    return 0


if __name__ == "__main__":
    sys.exit(main())
