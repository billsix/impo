# A Go quiz web page: timed multiple-choice questions to test students

**Status:** proposed — needs go-ahead (open questions below)
**Priority:** 5
**Difficulty:** 5 (a small Go server; the question bank comes from the literacy-test task)
**Created:** 2026-11-21 (William Emerison Six <billsix@gmail.com>)

## BLUF

Write a small web app in Go where a student takes a **multiple-choice quiz** with a **time limit per
question**, since how fast a student answers matters as well as whether they are right. It records,
per question, the answer, whether it was right, and how long it took, and shows a results page per
strand (topic), the same strands as the printed literacy tests. Done = a single Go binary that
serves the quiz from an embedded question bank, runs in this repo's container template, has tests,
and shows the maintainer each student's results.

## Context

- Read first: `CLAUDE.md`, and `tasks/math-literacy-tests-latex.md`. That task defines the question
  bank as data (strand, difficulty, stem, choices, answer, worked solution, sympy check). The quiz
  reads the same data, so the printed tests and the quiz never drift. Build that schema first, or at
  least agree on it.
- Design (proposed):
  - Go standard library only (`net/http`, `html/template`, `embed`, `encoding/json`), so no
    JavaScript build and no third-party dependencies; a small amount of plain JavaScript for the
    countdown, with the **server** enforcing the time limit (an answer that arrives after the
    deadline, measured by the server, counts as timed out).
  - One question per page; choices shuffled; no going back.
  - Results: correct/incorrect + seconds per question, summarized per strand ("solid / shaky / not
    yet", with speed). Stored per student (a JSON file per attempt, or SQLite).
  - Students identified by a name typed at the start (no passwords) unless Open question 2 says
    otherwise.
- **Hosting:** a Go server cannot run on GitHub Pages (static only). It runs on a machine on the home
  network (the maintainer's Pi or a desktop) or in a container. Open question 1.
- Go is not yet in this repo's images. It needs a Go toolchain image (Fedora `golang`) and the
  usual `make` targets (`image`, `run`, `test`, `format` with `gofmt`, `vet`).

## Plan

1. Agree on the question-bank schema with the literacy-test task.
2. Server + templates + per-question timer + results; `go test` for the timer rule and scoring.
3. Container + `make run` / `make test`; try it with the prealgebra bank.

## Open questions

1. **Where does it run?** (a) on the home network only (the Pi or a desktop), or (b) on the public
   internet (needs logins, HTTPS, abuse limits)? *Recommend (a).*
2. **Student identity:** a typed name is enough, or does each child need a password so they can't
   see each other's results? *Recommend a typed name plus an admin page for you behind one password.*
3. **Time limit:** one fixed limit per question (e.g. 60 s), or a limit per difficulty set in the
   question bank? *Recommend per difficulty, stored in the bank.*
4. **Where in the repo:** inside impo's proposed `study/` folder, or its own repository (a Go web app
   is a different kind of project from the book ports)? *Recommend its own repo, reading the bank
   from impo; you'd create it and add its `github` remote.*
