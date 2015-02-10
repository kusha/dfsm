##FSM determinization### Input format
	# Input FSM example	({s, p,q,r ,nonTermState, # unreachable state	fin1}, # finite state	{’a’, ’’’’, ’{’, ’)’, ’b’,’č’,’b’ }, {s ’č’ -> p,	q’a’ -> r, q’{’-> r, r ’a’ ->r, p’’’’ ->q ,	r ’’->s # rule without input symbol; also: r ’’ -> s },	# start state:	r	, {fin1, s, r} ) # finite states set	# ant other comments/whitelines
### Errors
#### Syntax errors
In case of wrong input format. Return code is 40.
#### Semantic errors
Return code is 41. In this cases:

1. Empty input alphabet
2. Rule contains symbol, which is not inside input alphabet
3. Start state not inside states set
4. Finite states is not all states subset### Usage


Parameter | Description |
---|---
--help | prints help message--input=filename | input file, UTF-8--output=filename | output file, UTF-8; equivalent FSM-e, --no-epsilon-rules | removes empty rules (not compatiable with -d)-d, --determinization | determinized FSM (not compatiable with -e)-i, --case-insensitive | case-insensitive input--analyze-string="myString" | (not compatiable with -e and -d) prints 1 if strings is acceptable by FSM, else 0*Realization description in DKA-doc.pdf.*