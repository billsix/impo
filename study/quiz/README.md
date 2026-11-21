# quiz — timed multiple-choice quizzes on the home network

A Go (standard library only) web server that gives the literacy tests' multiple-choice
questions (`study/bank/`) one at a time, each with a time limit set by its difficulty. The
**server** times every answer: one that arrives after the limit (plus a 2 s network grace)
counts as timed out and wrong, whatever the page's countdown showed, and a question cannot
be answered again or revisited. Students type a name; results per strand (solid / shaky /
not yet, with mean time) are shown at the end and kept as one JSON file per attempt in
`data/`. `/admin` lists every attempt behind one password.

```sh
make test                                   # [HOST] gofmt check, go vet, go test (container)
make build                                  # [HOST] ./quiz with the banks embedded
QUIZ_ADMIN_PASSWORD=... ./quiz -addr :8080  # [PI/DESKTOP] serve; results in ./data
QUIZ_ADMIN_PASSWORD=... make run            # [HOST] or serve from the container on PORT=8080
```

> Home network only: requests from addresses that are not loopback, private (192.168.x,
> 10.x, 172.16–31.x, fd00::/8) or link-local get 403 (`-allow-public` turns that off). There
> is no TLS, so do not forward the port to the internet.

Flags: `-addr`, `-data` (results dir), `-bank DIR` (read banks from a directory instead of
the embedded copy). After editing a bank: `make -C .. bank` then `make build`.
