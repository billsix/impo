# study — literacy tests, cliff notes, problem notebooks, quiz

Study material built from the impo books. Everything runs in podman containers from this
directory; outputs land in `output/`. Background and contracts: `study/CLAUDE.md`.

```sh
make test                                   # [HOST] the gate: lint, types, every answer sympy-checked
make literacy-tests                         # [HOST] output/literacy/<subject>{,-key,-scoring}.pdf
make cliff-notes                            # [HOST] output/cliff-notes/<subject>.pdf
make bank                                   # [HOST] regenerate bank/json/ after editing bank/*.toml
make problem-notebooks BOOK=prealgebra-2e   # [HOST] output/notebooks/prealgebra-2e/*.ipynb, executed
make -C quiz test && make -C quiz build     # [HOST] the quiz server (see quiz/README.md)
```

> `make problem-notebooks` needs the book's converted LaTeX first:
> `cd ../openstax/osbooks-prealgebra-bundle && ./fetch.sh && ./apply.sh && make convert`.

Subjects: `prealgebra`, `algebra-1`, `geometry` (Common Core), `algebra-2` (= OpenStax
Intermediate Algebra 2e). Questions and examples are MIT; material derived from OpenStax
books is CC BY 4.0 and attributed in each output.
