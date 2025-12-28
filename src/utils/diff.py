"""
Diff Utilities
Generate visual diffs for approval gates

Supports:
- Plain text unified diff (terminal display)
- HTML side-by-side diff (web UI)
"""

from typing import List
from difflib import unified_diff, HtmlDiff


def create_text_diff(
    original: str,
    proposed: str,
    line_term: str = ""
) -> str:
    """
    Create unified diff (git-style)
    
    Args:
        original: Original text
        proposed: Proposed changes
        line_term: Line terminator
        
    Returns:
        Unified diff string
        
    Example output:
        --- original
        +++ proposed
        @@ -1,3 +1,3 @@
        -Old line
        +New line
         Unchanged line
    """
    original_lines = original.splitlines(keepends=True)
    proposed_lines = proposed.splitlines(keepends=True)
    
    diff = unified_diff(
        original_lines,
        proposed_lines,
        fromfile="original",
        tofile="proposed",
        lineterm=line_term
    )
    
    return "".join(diff)


def create_html_diff(
    original: str,
    proposed: str,
    from_desc: str = "Original",
    to_desc: str = "Proposed"
) -> str:
    """
    Create HTML side-by-side diff
    
    Args:
        original: Original text
        proposed: Proposed changes
        from_desc: Description for original
        to_desc: Description for proposed
        
    Returns:
        HTML string with styled diff table
    """
    differ = HtmlDiff(wrapcolumn=80)
    
    html = differ.make_file(
        original.splitlines(),
        proposed.splitlines(),
        fromdesc=from_desc,
        todesc=to_desc
    )
    
    return html


def create_inline_diff(original: str, proposed: str) -> str:
    """
    Create inline diff (no side-by-side)
    
    Shows + for additions, - for deletions
    Good for terminal/CLI display
    """
    original_lines = original.splitlines()
    proposed_lines = proposed.splitlines()
    
    diff = unified_diff(
        original_lines,
        proposed_lines,
        lineterm=""
    )
    
    result = []
    for line in diff:
        if line.startswith('---') or line.startswith('+++'):
            continue  # Skip file headers
        elif line.startswith('@@'):
            continue  # Skip hunk headers
        elif line.startswith('+'):
            result.append(f"+ {line[1:]}")  # Addition
        elif line.startswith('-'):
            result.append(f"- {line[1:]}")  # Deletion
        else:
            result.append(f"  {line}")  # Unchanged
    
    return "\n".join(result)


def count_changes(original: str, proposed: str) -> dict:
    """
    Count additions and deletions
    
    Returns:
        {
            "additions": int,
            "deletions": int,
            "changes": int
        }
    """
    original_lines = set(original.splitlines())
    proposed_lines = set(proposed.splitlines())
    
    additions = len(proposed_lines - original_lines)
    deletions = len(original_lines - proposed_lines)
    
    return {
        "additions": additions,
        "deletions": deletions,
        "changes": additions + deletions
    }
