# Lab 5 — Static Analysis Issues: `society_dues.py`

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| SQL injection via f-string | Security (Bandit B608) | 9 | `addDue` built the INSERT statement with an f-string, splicing `flat`, `month` and `amount` directly into the SQL text. A flat or month value containing a quote (e.g. `') ; DROP TABLE dues; --`) could alter the query. | Replaced the f-string with a parameterized query (`?` placeholders) and passed the values as a tuple to `conn.execute`, letting sqlite3 handle escaping. |
| Use of `eval()` on arbitrary input | Security (Bandit B307) | 21 | `penalty(rule)` passed the `rule` string straight to `eval()`. Since `rule` could come from outside the program, this allows arbitrary code execution, not just arithmetic. | Replaced `eval` with a small AST-based evaluator (`ast.parse` + a whitelist of `+ - * /` on numeric literals) so only simple arithmetic expressions can be evaluated — anything else safely falls back to `0`. |
| Mutable default argument `history=[]` | Bug / Code smell (Pylint W0102) | 8 | Using a list literal as a default argument means the *same* list object is reused and silently accumulates entries across every call that doesn't pass its own `history`, which is a classic Python bug. | Changed the default to `history=None` and created a new list inside the function body when `history is None`. |
| Hardcoded password string | Security (Bandit B105) | 5 | `TREASURER_PASSWORD = "flat#101"` stored a credential as a literal in source code, where it would be visible to anyone with repo access and end up in version control history. | Moved the value out of source code: it is now read from the `TREASURER_PASSWORD` environment variable (`os.environ.get(...)`), with no secret committed to the file. |
| `== None` / `!= None` comparison | Style (Pylint C0121, Flake8 E711) | 29 | `pending()` used `rows != None` instead of the idiomatic `is not None`, which is flagged because `!=`/`==` can be overridden by custom `__eq__` methods and is not the correct way to check identity with `None`. | Changed to `rows is not None`. |
| Missing docstrings, non-snake_case name, long lines, no blank-line separation between functions | Style / readability (Pylint C0114/C0116/C0103/C0301, Flake8 E302/E501) | 1, 8, 12, 13, 15, 19, 27, 34 | The module and every function lacked docstrings, `addDue` used camelCase instead of `snake_case`, several lines exceeded 79–100 characters, and functions weren't separated by two blank lines (PEP 8). | Added a module docstring and a docstring to every function, renamed `addDue` to `add_due`, reformatted the parameterized SQL/strings onto multiple shorter lines, and added proper blank-line spacing between function definitions. |
| Inconsistent return statements | Code smell (Pylint R1710) | 12–16 | `collect()` returned `row[0]` on the success path but returned nothing (implicit `None`) when no row was found, which Pylint flags as an inconsistent-return pattern that can confuse callers. | Added an explicit `return None` for the "not found" branch so both paths consistently return a value. |

## Summary of runs

| Tool | Before | After |
|---|---|---|
| Pylint | 5.81/10 | **10.00/10** |
| Bandit | 1 Low + 2 Medium issues | **0 issues** |
| Flake8 | 5 warnings | **0 warnings** |

Raw reports are saved as `pylint_report.txt` / `bandit_report.txt` / `flake8_report.txt` (before) and
`pylint_report_after.txt` / `bandit_report_after.txt` / `flake8_report_after.txt` (after).
