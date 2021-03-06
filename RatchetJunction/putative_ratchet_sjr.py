import pysam
from load_genome import load_genome
from seq import Seq
import sys

"""
Finds all reads in the given samfile that are broken and have a
5'ss aligning to a known 5'ss and a 3'ss aligning upstream of
a known 3'ss for the given intron. And have an AGGT at 3' end.

Constrains that abs(5' - 3') is greater than MIN_INTRON_SIZE.

Need to tune expression for strand based on geometry of library.
"""

def merge_blocks(blocks):
	"""
	Removes short gaps in read that are likely indels
	"""
	i = 1
	while i < len(blocks) - 1:
		if blocks[i][0] - blocks[i-1][1] < 5:
			blocks[i] = (blocks[i][0], blocks[i+1][1])
			blocks.remove(blocks[i+1])
		else:
			i += 1
	return blocks

def get_jxns(anno_file):
	out = {}
	with open(anno_file) as fp:
		for line in fp:
			chrom, start, end, name, score, strand = line.strip().split('\t')[:6]
			if strand == '+':
				five, three, compare = int(start), int(end), max
			else:
				three, five, compare = int(start), int(end), min

			if abs(five-three) < MIN_INTRON_SIZE: continue

			key = (chrom, strand, five)
			out[key] = compare(out[key], three) if key in out else three
	return out

###############################################################

MIN_RECURSIVE_INTRON_SIZE = 35
MIN_INTRON_SIZE = 1000

samfile = pysam.AlignmentFile(sys.argv[1], 'rb')
ss = get_jxns(sys.argv[2])
seq = Seq(load_genome(open(sys.argv[3], 'r')))

for read in samfile.fetch():
	blocks = merge_blocks(read.get_blocks())
	strand = (read.is_read1 == read.is_reverse)
	if len(blocks) > 1:
		for i in xrange(len(blocks) - 1):
			if strand:
				five, three = blocks[i][1], blocks[i+1][0]
			else:
				three, five = blocks[i][1], blocks[i+1][0]

			# Some insertion events align to 5'ss and cause false positives
			# ... easily fixed by asserting a minimum recursive intron length.
			if abs(five - three) < MIN_RECURSIVE_INTRON_SIZE: continue

			chrom = samfile.getrname(read.reference_id)
			if chrom[:3] == 'chr': chrom = chrom[3:]
			strand_str = '+' if strand else '-'

			if (chrom, strand_str, five) in ss:
				intron_three = ss[(chrom, strand_str, five)]
				if strand and three < intron_three and seq.query(chrom, strand, three):
					print '\t'.join(map(str, [chrom, five, three, read.query_name, blocks, strand_str]))
				elif not strand and three > intron_three and seq.query(chrom, strand, three):
					print '\t'.join(map(str,[chrom, three, five, read.query_name, blocks, strand_str]))
