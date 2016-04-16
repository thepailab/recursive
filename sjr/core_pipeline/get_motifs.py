from load_genome import revcomp
from math import log

def get_pwm(seqs):
	length = len(seqs[0])
	pwm = [{'A': 1, 'C': 1, 'G': 1, 'T': 1} for i in range(length)]
	for seq in seqs:
		for i, char in enumerate(seq):
			if char not in pwm[i]: continue
			pwm[i][char] += 1

	for pos in range(length):
		for char in pwm[pos]:
			pwm[pos][char] = pwm[pos][char] / float(len(seqs))

	return pwm

def make_pwm(ss, genome):
	ss = open(ss, 'r')

	fives = {'+': {}, '-': {}}
	threes = {'+': {}, '-': {}}

	for line in ss:
		chrom, start, end, strand = line.strip().split('\t')
		chrom = chrom[3:]
		if strand == '+':
			five, three = int(start), int(end)
		else:
			three, five = int(start), int(end)

		if chrom in fives[strand]:
			fives[strand][chrom].add(five)
		else:
			fives[strand][chrom] = set([five])

		if chrom in threes[strand]:
			threes[strand][chrom].add(three)
		else:
			threes[strand][chrom] = set([five])

	fps = []
	tps = []
	for chrom in fives['+']:
		for pos in fives['+'][chrom]:	
			fps += [genome[chrom][pos+1:pos+9]]

	for chrom in threes['+']:
		for pos in threes['+'][chrom]:
			tps += [genome[chrom][pos-15: pos]]


	for chrom in fives['-']:
		for pos in fives['-'][chrom]:
			fps += [revcomp(genome[chrom][pos-8: pos])]

	for chrom in threes['-']:
		for pos in threes['-'][chrom]:
			tps += [revcomp(genome[chrom][pos+1:pos+16])]


	return get_pwm(fps), get_pwm(tps)

def get_min_score(pwm):
	bits = 0
	for w in pwm:
		p = min([w[c] for c in w])
		bits += log(p / 0.25, 2)
	return bits

def get_max_score(pwm):
	bits = 0
	for w in pwm:
		p = max([w[c] for c in w])
		bits += log(p / 0.25, 2)
	return bits


def score_motif(pwm, seq):
	assert len(pwm) == len(seq)
	bits = 0
	for w, c in zip(pwm, seq):
		if c == 'N': return 0
		bits += log(w[c] / 0.25, 2)
	return bits

