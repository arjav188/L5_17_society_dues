# Lab 5 — Reflection

**1. Which issue surprised you the most, and why?**

The mutable default argument (`history=[]`) in `addDue` surprised me the most. The code looks
completely reasonable at a glance — it reads like "if nobody passes a history list, start with an
empty one" — but Python only evaluates default argument expressions *once*, when the function is
defined, not each time it's called. That means every call to `addDue()` that relies on the default
was silently appending to the *same* list object across the entire program's lifetime. It's the
kind of bug that wouldn't show up in a quick manual test (the demo in `main()` doesn't even notice
it), but it would cause very confusing, hard-to-reproduce state leaks in a real deployment where
the function gets called many times.

**2. Which tool (Pylint, Flake8, or Bandit) found the issue you consider most severe, and what made it severe?**

Bandit found the most severe issue: the SQL injection vulnerability (B608) in `addDue`, caused by
building the `INSERT` statement with an f-string instead of parameterized placeholders. It's the
most severe because it's a correctness *and* security problem that scales with how the program is
used — if `flat` or `month` ever came from user input (a web form, an API, a CSV upload from a
resident), a crafted value could corrupt or exfiltrate the database, not just produce a wrong
answer. Flake8 and Pylint mostly caught style and maintainability issues; Bandit caught something
that could actually be exploited.

**3. Did fixing one issue ever reveal or create another? Describe what happened.**

Yes. Fixing the `eval()` security issue wasn't as simple as swapping in `ast.literal_eval` and
moving on. `ast.literal_eval` only parses literal values (numbers, strings, tuples, etc.) — it
cannot evaluate an expression like `"50 * 2"`, because multiplication isn't a literal. When I made
that swap, `penalty("50 * 2")` silently started returning `0` instead of `100`, which changed the
program's output and would have been a correctness regression. I had to write a small
AST-walking evaluator that explicitly whitelists numeric constants and the `+ - * /` operators, so
the function keeps doing real arithmetic while still rejecting anything that isn't plain math
(so it can't be abused the way raw `eval()` could).

**4. How would you build one of these checks (Pylint, Flake8, or Bandit) into a habit for future projects, so issues like these are caught earlier?**

I'd wire the relevant tool into two places: a pre-commit hook (via the `pre-commit` framework) that
runs `flake8` and `bandit` automatically before any commit is accepted, and a CI pipeline step that
runs `pylint`, `flake8`, and `bandit` on every pull request so issues are visible in code review
before merging, not discovered later. I'd also configure my editor (VS Code / PyLance) to show
Pylint/Flake8 warnings inline while typing, so problems like the mutable default argument or an
`== None` comparison get flagged within seconds rather than at commit time. Setting a minimum
Pylint score threshold (e.g. fail CI below 9.0) would also keep the codebase from drifting back
toward a low score over time.
