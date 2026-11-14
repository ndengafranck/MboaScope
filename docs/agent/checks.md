# Setup checks (Lead assistant log)

| Step | Check | Result | Evidence |
| --- | --- | --- | --- |
| 1 | gh auth | PASS | logged in as yannx8; scopes repo, workflow, read:org; `project` scope missing |
| 1 | git | PASS | 2.50.1 |
| 1 | Python 3.10+ | PASS | 3.14.2 |
| 1 | Node 22 or newer | PASS | v24.22.1 |
| 1 | make | PASS | installed (chocolatey); plain commands also documented in README |
| 2 | repo created | PASS | https://github.com/yannx8/MboaScope, topics set |
| 3-5 | contract schemas and test | PASS | `python -m pytest -q`: 12 passed, 4 skipped (annual and gpcp CSVs not present yet) |
| 4 | make mock | PASS | 24300 rows, 300 months, access_method mock |
| 6 | web build | PASS | `npm run build` OK, 220 kB JS |
| 7 | CI green on GitHub | PASS | job `ci` success on main |
| 7 | Pages deployed | PASS | https://yannx8.github.io/MboaScope/ serves the app and data/*.json (HTTP 200) |
| 9 | 26 issues, numbers match TEAM.md section 4 | PASS | #21 creation hit a network timeout; #21-#26 were edited and recreated so titles match the table |
| 9 | project board | UNRESOLVED | token lacks `project` scope; manual steps given to the Lead |
| 10 | collaborators | PARTIAL | yannsamir22 and Firminfire are collaborators; invitations pending for ndengafranck and Paveljuniorr (an earlier invite to the misspelled ndengafrank was cancelled); invitation pending for excellenttheophile4-byte |
| 10 | branch protection on main | PASS | PR required, status check `ci`, no force-push, no deletion, 0 approvals |
| 11 | secrets scan | PASS | `git grep -i "api_key\|password"` shows variable names only |
| 11 | make setup | PARTIAL | steps run individually (venv, pip install, npm ci/install); pip needed a longer timeout on this network |
| - | Pages mock banner | UNRESOLVED | not viewed in a browser; data files flagged is_mock true and served |
