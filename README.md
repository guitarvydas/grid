# grid

# usage
`./@make`

# status
@make calls @makec which contains the custom script for this project

2026-02-27 - @makec inhales `tests.grid` and exhales slighly modified file - not legal .grid code, but an intermediate form where:
- newlines are transformed to `⎩ ... ⎭` syntax to make them visible, and to include the source file line number
- comments are transfomed to `⎝ ... ⎠`
- keywords are lower-cased
- identifiers are lower-cased
- strings and comments retain original case
- the intermediate code is machine readable but not particularly human readable (aka ugly)

prepass is done by using ${PBP}/t2t with `prepass.ohm` and `prepass.rwr` (see @makec)
(t2t script is in subdirectory ./pbp/, @make sets ${PBP} to point to the subdirectory - @make sets up shell variables, then calls @makec)

(waiting for response on whether OhmJS v18 can ignore whitespace and comments, but keep them and re-emit them ; if not, then we need to manually add them to the grammar)

# next step
rewrite grammar keeping above in mind, the grammar should be significantly simpler

