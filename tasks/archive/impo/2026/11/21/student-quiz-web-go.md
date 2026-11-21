# A Go quiz web page: timed multiple-choice questions to test students

**Done 2026-11-21** (branch `study-and-publishing`). Not yet run on the maintainer's Pi or tried
by a student. Usage: `study/quiz/README.md`; state: `tasks/reference/study/status.md`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-21: "go with your recommendations")

- Home network only; students type a name; one admin password; time limit per difficulty, stored in
  the question bank; in impo at `study/quiz/` with its own image, `Makefile` and gates.

## Choices made while building (the maintainer was away)

- **Reads the literacy-test bank** (`study/bank/json/*.json`, the generated committed copy) and quizzes
  its part-A questions; `make bank` copies them into `quiz/bank/` (gitignored) to embed, and `-bank DIR`
  reads a directory instead. Stems and choices are pre-rendered HTML + MathML, so the browser needs no
  JavaScript math library.
- **The server times every answer:** a question's clock starts the first time it is served (a reload
  does not restart it); an answer later than its limit + 2 s grace counts as timed out and wrong; a
  question that is not the current one cannot be answered (no going back, no double submits). The page's
  countdown only auto-submits.
- Question order and each question's choices are shuffled per attempt (math/rand), attempt ids are
  random 128-bit tokens, and every attempt is saved after each answer as `data/<id>.json` (atomic
  rename) and reloaded at start.
- Results per strand: right/total, timed-out count, mean seconds, band (solid ≥ 80 %, shaky ≥ 50 %, not
  yet), plus per question. `/admin`: HTTP basic auth, any user name, password from
  `QUIZ_ADMIN_PASSWORD` (constant-time compare; no password = admin off).
- "Home network only" is enforced too: requests from non-loopback, non-private, non-link-local
  addresses get 403 unless `-allow-public`. No TLS (documented: do not forward the port).

## What was built

`study/quiz/`: `main.go`, `bank.go`, `attempt.go`, `server.go`, `templates/*.html`,
`quiz_test.go` + `testdata/mini.json`, `Dockerfile` (Fedora 45 + golang), `Makefile` (`test`, `build`,
`run`, `format`, `bank`), `README.md`, `.gitignore`.

## Verification

- `make -C study/quiz test` (container): exit 0 — `gofmt -l` empty, `go vet` clean, `go test` (12
  tests: in-time and late answers, clock not restarted by reload, no going back, bands, per-strand
  score, private-address filter, a whole quiz over HTTP with the saved attempt reloaded, admin auth,
  403 for a public address, bank loading).
- Smoke run of the built binary with the four real banks: home page lists the subjects, starting an
  algebra-2 attempt serves question 1 of 24 with its strand, `/admin` with the password lists it.
