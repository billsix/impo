// Command quiz serves timed multiple-choice quizzes from the impo literacy-test
// question bank (study/bank/), for students on a home network.
//
// Each question has a time limit set by its difficulty (stored in the bank);
// the server times every answer and counts a late one as wrong. A student types
// a name to start; results are kept per attempt as JSON under -data, shown to
// the student at the end, and listed for the admin at /admin (HTTP basic auth,
// any user name, the password from QUIZ_ADMIN_PASSWORD). Requests from outside
// loopback / private / link-local addresses are refused unless -allow-public.
package main

import (
	"flag"
	"log"
	"net/http"
	"os"
	"time"
)

func main() {
	addr := flag.String("addr", ":8080", "listen address")
	bankDir := flag.String("bank", "", "read the banks from this directory instead of the embedded copy")
	dataDir := flag.String("data", "data", "directory for the attempt results (JSON)")
	allowPublic := flag.Bool("allow-public", false, "also serve non-private addresses (not recommended)")
	flag.Parse()

	banks, err := openBanks(*bankDir)
	if err != nil {
		log.Fatal(err)
	}
	password := os.Getenv("QUIZ_ADMIN_PASSWORD")
	if password == "" {
		log.Print("QUIZ_ADMIN_PASSWORD is not set: the /admin page is disabled")
	}
	server, err := NewServer(banks, *dataDir, password, *allowPublic)
	if err != nil {
		log.Fatal(err)
	}
	log.Printf("quiz: %d subject(s) %v on %s, results in %s", len(banks), subjects(banks), *addr, *dataDir)
	httpServer := &http.Server{Addr: *addr, Handler: server.Handler(), ReadHeaderTimeout: 10 * time.Second}
	log.Fatal(httpServer.ListenAndServe())
}
