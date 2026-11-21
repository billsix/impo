package main

import (
	"embed"
	"encoding/json"
	"fmt"
	"io/fs"
	"os"
	"path"
	"sort"
	"strings"
)

// embeddedBanks holds the question banks copied from ../bank/json/ by
// `make bank` (plus bank/README.txt, so the directory is never empty).
//
//go:embed bank
var embeddedBanks embed.FS

// Choice is one multiple-choice option, in LaTeX and in HTML (MathML).
type Choice struct {
	Tex  string `json:"tex"`
	HTML string `json:"html"`
}

// Question is one bank question. Only part "A" (multiple choice) is quizzed;
// Answer is the index into Choices of the right one.
type Question struct {
	ID         string   `json:"id"`
	Part       string   `json:"part"`
	Strand     string   `json:"strand"`
	Difficulty int      `json:"difficulty"`
	StemHTML   string   `json:"stem_html"`
	Solution   string   `json:"solution_html"`
	Choices    []Choice `json:"choices"`
	Answer     int      `json:"answer"`
}

// Strand is one topic of a subject, with the book sections to review.
type Strand struct {
	ID     string   `json:"id"`
	Name   string   `json:"name"`
	Review []string `json:"review"`
}

// Bank is one subject's question bank, as study/tools/bank.py exports it.
type Bank struct {
	Subject    string         `json:"subject"`
	Title      string         `json:"title"`
	TimeLimits map[string]int `json:"time_limits"`
	Strands    []Strand       `json:"strands"`
	Questions  []Question     `json:"questions"`
}

// MultipleChoice returns the bank's part-A questions, in bank order.
func (b *Bank) MultipleChoice() []Question {
	var out []Question
	for _, q := range b.Questions {
		if q.Part == "A" {
			out = append(out, q)
		}
	}
	return out
}

// TimeLimit returns the seconds allowed for a question of the given difficulty.
func (b *Bank) TimeLimit(difficulty int) (int, error) {
	seconds, ok := b.TimeLimits[fmt.Sprint(difficulty)]
	if !ok || seconds <= 0 {
		return 0, fmt.Errorf("%s: no time limit for difficulty %d", b.Subject, difficulty)
	}
	return seconds, nil
}

// StrandName returns a strand's display name (its id when unknown).
func (b *Bank) StrandName(id string) string {
	for _, s := range b.Strands {
		if s.ID == id {
			return s.Name
		}
	}
	return id
}

// validate checks what the server relies on: limits for every difficulty and
// an answer index inside the choices.
func (b *Bank) validate() error {
	if len(b.MultipleChoice()) == 0 {
		return fmt.Errorf("%s: no multiple-choice questions", b.Subject)
	}
	for _, q := range b.MultipleChoice() {
		if _, err := b.TimeLimit(q.Difficulty); err != nil {
			return err
		}
		if q.Answer < 0 || q.Answer >= len(q.Choices) {
			return fmt.Errorf("%s: answer index %d out of range", q.ID, q.Answer)
		}
	}
	return nil
}

// loadBanks reads every *.json bank in fsys (non-JSON files are ignored),
// keyed by subject.
func loadBanks(fsys fs.FS) (map[string]*Bank, error) {
	banks := map[string]*Bank{}
	entries, err := fs.ReadDir(fsys, ".")
	if err != nil {
		return nil, err
	}
	for _, entry := range entries {
		if entry.IsDir() || !strings.HasSuffix(entry.Name(), ".json") {
			continue
		}
		data, err := fs.ReadFile(fsys, entry.Name())
		if err != nil {
			return nil, err
		}
		var b Bank
		if err := json.Unmarshal(data, &b); err != nil {
			return nil, fmt.Errorf("%s: %w", entry.Name(), err)
		}
		if err := b.validate(); err != nil {
			return nil, err
		}
		banks[b.Subject] = &b
	}
	if len(banks) == 0 {
		return nil, fmt.Errorf("no question banks found (run make bank)")
	}
	return banks, nil
}

// openBanks loads the banks from dir, or from the embedded copy when dir is "".
func openBanks(dir string) (map[string]*Bank, error) {
	if dir != "" {
		return loadBanks(os.DirFS(dir))
	}
	sub, err := fs.Sub(embeddedBanks, path.Clean("bank"))
	if err != nil {
		return nil, err
	}
	return loadBanks(sub)
}

// subjects returns the bank subjects in sorted order.
func subjects(banks map[string]*Bank) []string {
	var out []string
	for s := range banks {
		out = append(out, s)
	}
	sort.Strings(out)
	return out
}
