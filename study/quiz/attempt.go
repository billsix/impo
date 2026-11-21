package main

import (
	"errors"
	"math/rand"
	"time"
)

// Grace is the network allowance added to every time limit: an answer that
// reaches the server later than limit+Grace after the question was served
// counts as timed out (and wrong), whatever the browser's countdown showed.
const Grace = 2 * time.Second

// Score bands, as a fraction of a strand's questions answered right in time
// (the same bands as the printed tests' scoring sheet).
const (
	SolidAt = 0.8
	ShakyAt = 0.5
)

// Answer records one answered (or timed-out) question.
type Answer struct {
	QuestionID string  `json:"question_id"`
	Strand     string  `json:"strand"`
	Chosen     int     `json:"chosen"` // bank choice index; -1 when none was chosen
	Correct    bool    `json:"correct"`
	TimedOut   bool    `json:"timed_out"`
	Seconds    float64 `json:"seconds"`
	Limit      int     `json:"limit_seconds"`
}

// Attempt is one student's run through one subject's multiple-choice questions:
// one question at a time, no going back, each timed by the server.
type Attempt struct {
	ID        string    `json:"id"`
	Student   string    `json:"student"`
	Subject   string    `json:"subject"`
	Started   time.Time `json:"started"`
	Finished  time.Time `json:"finished"`
	Order     []int     `json:"order"`        // bank part-A question indexes, in asked order
	Choices   [][]int   `json:"choice_order"` // per asked question: displayed slot -> bank choice
	Current   int       `json:"current"`      // index into Order of the question being asked
	ServedAt  time.Time `json:"served_at"`    // when Current was first shown (zero: not yet)
	Answers   []Answer  `json:"answers"`
	questions []Question
}

// ErrNotCurrent rejects an answer to any question but the current one.
var ErrNotCurrent = errors.New("not the current question")

// ErrNotServed rejects an answer to a question that was never shown.
var ErrNotServed = errors.New("question was not served")

// NewAttempt shuffles the subject's multiple-choice questions and each
// question's choices with rng.
func NewAttempt(id, student string, bank *Bank, now time.Time, rng *rand.Rand) *Attempt {
	questions := bank.MultipleChoice()
	order := rng.Perm(len(questions))
	choices := make([][]int, len(order))
	for i, qi := range order {
		choices[i] = rng.Perm(len(questions[qi].Choices))
	}
	return &Attempt{
		ID: id, Student: student, Subject: bank.Subject, Started: now,
		Order: order, Choices: choices, questions: questions,
	}
}

// Done reports whether every question has been answered.
func (a *Attempt) Done() bool { return a.Current >= len(a.Order) }

// Question returns the current question and its choices in displayed order.
func (a *Attempt) Question() (Question, []Choice) {
	q := a.questions[a.Order[a.Current]]
	shown := make([]Choice, len(q.Choices))
	for slot, ci := range a.Choices[a.Current] {
		shown[slot] = q.Choices[ci]
	}
	return q, shown
}

// Serve marks the current question as shown at now, once: reloading the page
// does not restart its clock. It returns the deadline.
func (a *Attempt) Serve(bank *Bank, now time.Time) (time.Time, error) {
	q, _ := a.Question()
	limit, err := bank.TimeLimit(q.Difficulty)
	if err != nil {
		return time.Time{}, err
	}
	if a.ServedAt.IsZero() {
		a.ServedAt = now
	}
	return a.ServedAt.Add(time.Duration(limit) * time.Second), nil
}

// Submit records the answer to question number index (slot -1 = no choice),
// received by the server at now, and moves on to the next question.
func (a *Attempt) Submit(bank *Bank, index, slot int, now time.Time) (Answer, error) {
	if a.Done() || index != a.Current {
		return Answer{}, ErrNotCurrent
	}
	if a.ServedAt.IsZero() {
		return Answer{}, ErrNotServed
	}
	q, _ := a.Question()
	limit, err := bank.TimeLimit(q.Difficulty)
	if err != nil {
		return Answer{}, err
	}
	elapsed := now.Sub(a.ServedAt)
	timedOut := elapsed > time.Duration(limit)*time.Second+Grace
	chosen := -1
	if slot >= 0 && slot < len(a.Choices[a.Current]) {
		chosen = a.Choices[a.Current][slot]
	}
	answer := Answer{
		QuestionID: q.ID, Strand: q.Strand, Chosen: chosen,
		Correct:  !timedOut && chosen == q.Answer,
		TimedOut: timedOut, Seconds: elapsed.Seconds(), Limit: limit,
	}
	a.Answers = append(a.Answers, answer)
	a.Current++
	a.ServedAt = time.Time{}
	if a.Done() {
		a.Finished = now
	}
	return answer, nil
}

// StrandScore summarizes one strand of an attempt.
type StrandScore struct {
	Strand      string
	Name        string
	Right       int
	Total       int
	TimedOut    int
	MeanSeconds float64
	Band        string
}

// Band names a strand's result from the fraction answered right in time.
func Band(right, total int) string {
	if total == 0 {
		return "not asked"
	}
	switch fraction := float64(right) / float64(total); {
	case fraction >= SolidAt:
		return "solid"
	case fraction >= ShakyAt:
		return "shaky"
	default:
		return "not yet"
	}
}

// Score summarizes the answers per strand, in the bank's strand order.
func Score(bank *Bank, answers []Answer) []StrandScore {
	var out []StrandScore
	for _, s := range bank.Strands {
		score := StrandScore{Strand: s.ID, Name: s.Name}
		seconds := 0.0
		for _, a := range answers {
			if a.Strand != s.ID {
				continue
			}
			score.Total++
			seconds += a.Seconds
			if a.Correct {
				score.Right++
			}
			if a.TimedOut {
				score.TimedOut++
			}
		}
		if score.Total > 0 {
			score.MeanSeconds = seconds / float64(score.Total)
		}
		score.Band = Band(score.Right, score.Total)
		out = append(out, score)
	}
	return out
}
