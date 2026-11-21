The quiz server embeds this directory. `make bank` (in study/quiz/) copies the
generated question banks from ../bank/json/*.json here before building; the
copies are gitignored. The source of the questions is study/bank/<subject>.toml.
