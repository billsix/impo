package main

import (
	"math/rand"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"strconv"
	"strings"
	"testing"
	"time"
)

func miniBank(t *testing.T) *Bank {
	t.Helper()
	banks, err := loadBanks(os.DirFS("testdata"))
	if err != nil {
		t.Fatal(err)
	}
	return banks["mini"]
}

// rightSlot returns the displayed slot holding the right answer.
func rightSlot(a *Attempt) int {
	q, _ := a.Question()
	for slot, ci := range a.Choices[a.Current] {
		if ci == q.Answer {
			return slot
		}
	}
	return -1
}

func TestOnlyMultipleChoiceIsAsked(t *testing.T) {
	a := NewAttempt("id", "Ann", miniBank(t), time.Now(), rand.New(rand.NewSource(1)))
	if len(a.Order) != 2 {
		t.Fatalf("want 2 part-A questions, got %d", len(a.Order))
	}
}

func TestAnswerInTimeIsScored(t *testing.T) {
	bank := miniBank(t)
	start := time.Date(2026, 11, 21, 9, 0, 0, 0, time.UTC)
	a := NewAttempt("id", "Ann", bank, start, rand.New(rand.NewSource(1)))
	if _, err := a.Serve(bank, start); err != nil {
		t.Fatal(err)
	}
	ans, err := a.Submit(bank, 0, rightSlot(a), start.Add(10*time.Second))
	if err != nil || !ans.Correct || ans.TimedOut || ans.Seconds != 10 {
		t.Fatalf("got %+v, %v", ans, err)
	}
}

func TestLateAnswerTimesOutEvenIfRight(t *testing.T) {
	bank := miniBank(t)
	start := time.Now()
	a := NewAttempt("id", "Ann", bank, start, rand.New(rand.NewSource(2)))
	q, _ := a.Question()
	limit, _ := bank.TimeLimit(q.Difficulty)
	if _, err := a.Serve(bank, start); err != nil {
		t.Fatal(err)
	}
	late := start.Add(time.Duration(limit)*time.Second + Grace + time.Second)
	ans, err := a.Submit(bank, 0, rightSlot(a), late)
	if err != nil || ans.Correct || !ans.TimedOut {
		t.Fatalf("want timed out and wrong, got %+v, %v", ans, err)
	}
}

func TestReloadDoesNotRestartTheClock(t *testing.T) {
	bank := miniBank(t)
	start := time.Now()
	a := NewAttempt("id", "Ann", bank, start, rand.New(rand.NewSource(3)))
	first, _ := a.Serve(bank, start)
	again, _ := a.Serve(bank, start.Add(30*time.Second))
	if !first.Equal(again) {
		t.Fatalf("deadline moved from %v to %v", first, again)
	}
}

func TestNoGoingBack(t *testing.T) {
	bank := miniBank(t)
	now := time.Now()
	a := NewAttempt("id", "Ann", bank, now, rand.New(rand.NewSource(4)))
	if _, err := a.Submit(bank, 0, 0, now); err != ErrNotServed {
		t.Fatalf("answer before serving: want ErrNotServed, got %v", err)
	}
	_, _ = a.Serve(bank, now)
	if _, err := a.Submit(bank, 0, 0, now); err != nil {
		t.Fatal(err)
	}
	if _, err := a.Submit(bank, 0, 1, now); err != ErrNotCurrent {
		t.Fatalf("re-answer: want ErrNotCurrent, got %v", err)
	}
}

func TestBands(t *testing.T) {
	cases := map[[2]int]string{{4, 5}: "solid", {3, 5}: "shaky", {2, 5}: "not yet", {0, 0}: "not asked"}
	for in, want := range cases {
		if got := Band(in[0], in[1]); got != want {
			t.Errorf("Band(%d, %d) = %q, want %q", in[0], in[1], got, want)
		}
	}
}

func TestScoreByStrand(t *testing.T) {
	bank := miniBank(t)
	scores := Score(bank, []Answer{
		{Strand: "s1", Correct: true, Seconds: 4},
		{Strand: "s2", Correct: false, TimedOut: true, Seconds: 95},
	})
	if scores[0].Band != "solid" || scores[1].Band != "not yet" || scores[1].TimedOut != 1 {
		t.Fatalf("got %+v", scores)
	}
}

func TestIsLocal(t *testing.T) {
	for addr, want := range map[string]bool{
		"127.0.0.1:5000": true, "192.168.0.20:1": true, "10.1.2.3:1": true,
		"[::1]:80": true, "[fd00::1]:80": true, "8.8.8.8:53": false, "[2001:4860::1]:1": false,
	} {
		if got := isLocal(addr); got != want {
			t.Errorf("isLocal(%s) = %v, want %v", addr, got, want)
		}
	}
}

func newTestServer(t *testing.T) *Server {
	t.Helper()
	s, err := NewServer(map[string]*Bank{"mini": miniBank(t)}, t.TempDir(), "secret", false)
	if err != nil {
		t.Fatal(err)
	}
	return s
}

func do(t *testing.T, h http.Handler, method, target string, form url.Values) *httptest.ResponseRecorder {
	t.Helper()
	var body *strings.Reader
	if form != nil {
		body = strings.NewReader(form.Encode())
	} else {
		body = strings.NewReader("")
	}
	r := httptest.NewRequest(method, target, body)
	r.RemoteAddr = "192.168.1.5:4000"
	if form != nil {
		r.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	}
	w := httptest.NewRecorder()
	h.ServeHTTP(w, r)
	return w
}

func TestWholeQuizOverHTTP(t *testing.T) {
	s := newTestServer(t)
	h := s.Handler()
	w := do(t, h, http.MethodPost, "/start", url.Values{"name": {"Ann"}, "subject": {"mini"}})
	if w.Code != http.StatusSeeOther {
		t.Fatalf("start: %d %s", w.Code, w.Body)
	}
	next := w.Header().Get("Location")
	id := strings.TrimPrefix(next, "/q/")
	for i := 0; i < 2; i++ {
		if w = do(t, h, http.MethodGet, next, nil); w.Code != http.StatusOK {
			t.Fatalf("question %d: %d", i, w.Code)
		}
		slot := rightSlot(s.attempts[id])
		w = do(t, h, http.MethodPost, "/a/"+id, url.Values{"index": {strconv.Itoa(i)}, "choice": {strconv.Itoa(slot)}})
		next = w.Header().Get("Location")
	}
	w = do(t, h, http.MethodGet, next, nil)
	if w.Code != http.StatusSeeOther || w.Header().Get("Location") != "/r/"+id {
		t.Fatalf("finished quiz should redirect to results, got %d %s", w.Code, w.Header().Get("Location"))
	}
	w = do(t, h, http.MethodGet, "/r/"+id, nil)
	if !strings.Contains(w.Body.String(), "2 of 2 right") {
		t.Fatalf("results page: %s", w.Body)
	}
	if _, err := os.Stat(s.dataDir + "/" + id + ".json"); err != nil {
		t.Fatalf("attempt not saved: %v", err)
	}
	// A restarted server finds the saved attempt.
	again, err := NewServer(s.banks, s.dataDir, "secret", false)
	if err != nil || again.attempts[id] == nil {
		t.Fatalf("reload: %v", err)
	}
}

func TestAdminNeedsThePassword(t *testing.T) {
	h := newTestServer(t).Handler()
	if w := do(t, h, http.MethodGet, "/admin", nil); w.Code != http.StatusUnauthorized {
		t.Fatalf("no password: want 401, got %d", w.Code)
	}
	r := httptest.NewRequest(http.MethodGet, "/admin", nil)
	r.RemoteAddr = "127.0.0.1:1"
	r.SetBasicAuth("anyone", "secret")
	w := httptest.NewRecorder()
	h.ServeHTTP(w, r)
	if w.Code != http.StatusOK {
		t.Fatalf("right password: want 200, got %d", w.Code)
	}
}

func TestPublicAddressIsRefused(t *testing.T) {
	h := newTestServer(t).Handler()
	r := httptest.NewRequest(http.MethodGet, "/", nil)
	r.RemoteAddr = "8.8.8.8:1"
	w := httptest.NewRecorder()
	h.ServeHTTP(w, r)
	if w.Code != http.StatusForbidden {
		t.Fatalf("want 403, got %d", w.Code)
	}
}

func TestEmbeddedOrDirectoryBanksLoad(t *testing.T) {
	banks, err := openBanks("testdata")
	if err != nil || banks["mini"] == nil {
		t.Fatalf("openBanks(testdata): %v", err)
	}
}
