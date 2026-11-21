package main

import (
	"crypto/rand"
	"crypto/subtle"
	"embed"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"html/template"
	mathrand "math/rand"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"
	"unicode/utf8"
)

//go:embed templates/*.html
var templateFiles embed.FS

// Server is the quiz web app: the banks, the attempts (in memory, and one JSON
// file per attempt under dataDir), and the admin password.
type Server struct {
	banks         map[string]*Bank
	dataDir       string
	adminPassword string
	allowPublic   bool
	now           func() time.Time
	pages         *template.Template

	mu       sync.Mutex
	attempts map[string]*Attempt
	rng      *mathrand.Rand
}

// NewServer loads the existing attempts from dataDir (created if missing).
func NewServer(banks map[string]*Bank, dataDir, adminPassword string, allowPublic bool) (*Server, error) {
	pages, err := template.New("").Funcs(template.FuncMap{
		"trusted": func(s string) template.HTML { return template.HTML(s) }, // trusted bank content
		"letter":  func(i int) string { return string(rune('A' + i)) },
		"inc":     func(i int) int { return i + 1 },
		"seconds": func(f float64) string { return strconv.FormatFloat(f, 'f', 1, 64) },
	}).ParseFS(templateFiles, "templates/*.html")
	if err != nil {
		return nil, err
	}
	if err := os.MkdirAll(dataDir, 0o755); err != nil {
		return nil, err
	}
	s := &Server{
		banks: banks, dataDir: dataDir, adminPassword: adminPassword, allowPublic: allowPublic,
		now: time.Now, pages: pages, attempts: map[string]*Attempt{},
		rng: mathrand.New(mathrand.NewSource(time.Now().UnixNano())),
	}
	return s, s.loadAttempts()
}

func (s *Server) loadAttempts() error {
	files, err := filepath.Glob(filepath.Join(s.dataDir, "*.json"))
	if err != nil {
		return err
	}
	for _, file := range files {
		data, err := os.ReadFile(file)
		if err != nil {
			return err
		}
		var a Attempt
		if err := json.Unmarshal(data, &a); err != nil {
			return fmt.Errorf("%s: %w", file, err)
		}
		if bank, ok := s.banks[a.Subject]; ok {
			a.questions = bank.MultipleChoice()
			if len(a.questions) == 0 || maxIndex(a.Order) >= len(a.questions) {
				continue // the bank changed under this attempt; keep it on disk only
			}
			s.attempts[a.ID] = &a
		}
	}
	return nil
}

func maxIndex(order []int) int {
	m := -1
	for _, i := range order {
		if i > m {
			m = i
		}
	}
	return m
}

// save writes the attempt's JSON atomically (temp file + rename).
func (s *Server) save(a *Attempt) error {
	data, err := json.MarshalIndent(a, "", " ")
	if err != nil {
		return err
	}
	final := filepath.Join(s.dataDir, a.ID+".json")
	tmp := final + ".tmp"
	if err := os.WriteFile(tmp, data, 0o644); err != nil {
		return err
	}
	return os.Rename(tmp, final)
}

// Handler returns the app's routes behind the home-network filter.
func (s *Server) Handler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/", s.home)
	mux.HandleFunc("/start", s.start)
	mux.HandleFunc("/q/", s.question)
	mux.HandleFunc("/a/", s.answer)
	mux.HandleFunc("/r/", s.results)
	mux.HandleFunc("/admin", s.admin)
	return s.localOnly(mux)
}

// isLocal reports whether a remote address is on this machine or a private
// (home) network: loopback, RFC 1918 / RFC 4193 private, or link-local.
func isLocal(remoteAddr string) bool {
	host, _, err := net.SplitHostPort(remoteAddr)
	if err != nil {
		host = remoteAddr
	}
	ip := net.ParseIP(host)
	return ip != nil && (ip.IsLoopback() || ip.IsPrivate() || ip.IsLinkLocalUnicast())
}

func (s *Server) localOnly(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if !s.allowPublic && !isLocal(r.RemoteAddr) {
			http.Error(w, "this quiz is for the home network only", http.StatusForbidden)
			return
		}
		next.ServeHTTP(w, r)
	})
}

func (s *Server) render(w http.ResponseWriter, name string, data any) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	if err := s.pages.ExecuteTemplate(w, name, data); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

func (s *Server) home(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/" {
		http.NotFound(w, r)
		return
	}
	var list []*Bank
	for _, name := range subjects(s.banks) {
		list = append(list, s.banks[name])
	}
	s.render(w, "home.html", map[string]any{"Banks": list})
}

func newID() string {
	b := make([]byte, 16)
	if _, err := rand.Read(b); err != nil {
		panic(err) // crypto/rand failing is unrecoverable
	}
	return hex.EncodeToString(b)
}

func (s *Server) start(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Redirect(w, r, "/", http.StatusSeeOther)
		return
	}
	name := strings.TrimSpace(r.FormValue("name"))
	bank, ok := s.banks[r.FormValue("subject")]
	if name == "" || utf8.RuneCountInString(name) > 40 || !ok {
		http.Error(w, "type your name (up to 40 letters) and pick a subject", http.StatusBadRequest)
		return
	}
	s.mu.Lock()
	a := NewAttempt(newID(), name, bank, s.now(), s.rng)
	s.attempts[a.ID] = a
	err := s.save(a)
	s.mu.Unlock()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	http.Redirect(w, r, "/q/"+a.ID, http.StatusSeeOther)
}

func (s *Server) lookup(w http.ResponseWriter, r *http.Request, prefix string) *Attempt {
	a, ok := s.attempts[strings.TrimPrefix(r.URL.Path, prefix)]
	if !ok {
		http.NotFound(w, r)
		return nil
	}
	return a
}

func (s *Server) question(w http.ResponseWriter, r *http.Request) {
	s.mu.Lock()
	defer s.mu.Unlock()
	a := s.lookup(w, r, "/q/")
	if a == nil {
		return
	}
	if a.Done() {
		http.Redirect(w, r, "/r/"+a.ID, http.StatusSeeOther)
		return
	}
	bank := s.banks[a.Subject]
	deadline, err := a.Serve(bank, s.now())
	if err == nil {
		err = s.save(a)
	}
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	q, choices := a.Question()
	remaining := deadline.Sub(s.now()).Seconds()
	if remaining < 0 {
		remaining = 0
	}
	s.render(w, "question.html", map[string]any{
		"Attempt": a, "Bank": bank, "Question": q, "Choices": choices,
		"Number": a.Current + 1, "Count": len(a.Order), "Remaining": int(remaining),
		"Strand": bank.StrandName(q.Strand),
	})
}

func (s *Server) answer(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "POST only", http.StatusMethodNotAllowed)
		return
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	a := s.lookup(w, r, "/a/")
	if a == nil {
		return
	}
	index, err := strconv.Atoi(r.FormValue("index"))
	if err != nil {
		http.Error(w, "bad question index", http.StatusBadRequest)
		return
	}
	slot := -1
	if v := r.FormValue("choice"); v != "" {
		if slot, err = strconv.Atoi(v); err != nil {
			http.Error(w, "bad choice", http.StatusBadRequest)
			return
		}
	}
	_, err = a.Submit(s.banks[a.Subject], index, slot, s.now())
	switch {
	case errors.Is(err, ErrNotCurrent), errors.Is(err, ErrNotServed):
		// a stale or repeated submit (back button, double click): no going back
	case err != nil:
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	default:
		if err := s.save(a); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}
	http.Redirect(w, r, "/q/"+a.ID, http.StatusSeeOther)
}

// resultRow is one answered question as the results page shows it.
type resultRow struct {
	Number int
	Answer Answer
	Strand string
}

func (s *Server) resultsData(a *Attempt) map[string]any {
	bank := s.banks[a.Subject]
	var rows []resultRow
	right := 0
	for i, ans := range a.Answers {
		rows = append(rows, resultRow{Number: i + 1, Answer: ans, Strand: bank.StrandName(ans.Strand)})
		if ans.Correct {
			right++
		}
	}
	return map[string]any{
		"Attempt": a, "Bank": bank, "Scores": Score(bank, a.Answers), "Rows": rows,
		"Right": right, "Count": len(a.Answers), "Done": a.Done(),
	}
}

func (s *Server) results(w http.ResponseWriter, r *http.Request) {
	s.mu.Lock()
	defer s.mu.Unlock()
	a := s.lookup(w, r, "/r/")
	if a == nil {
		return
	}
	s.render(w, "results.html", s.resultsData(a))
}

// authorized checks HTTP basic auth against the one admin password (any user
// name); with no password configured the admin page is off.
func (s *Server) authorized(r *http.Request) bool {
	_, password, ok := r.BasicAuth()
	return s.adminPassword != "" && ok &&
		subtle.ConstantTimeCompare([]byte(password), []byte(s.adminPassword)) == 1
}

func (s *Server) admin(w http.ResponseWriter, r *http.Request) {
	if !s.authorized(r) {
		w.Header().Set("WWW-Authenticate", `Basic realm="quiz admin"`)
		http.Error(w, "admin password required", http.StatusUnauthorized)
		return
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	var list []map[string]any
	for _, a := range s.attempts {
		list = append(list, s.resultsData(a))
	}
	sort.Slice(list, func(i, j int) bool {
		return list[i]["Attempt"].(*Attempt).Started.After(list[j]["Attempt"].(*Attempt).Started)
	})
	s.render(w, "admin.html", map[string]any{"Attempts": list})
}
