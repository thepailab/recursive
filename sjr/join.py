import sys


cur_chrom, cur_start, cur_end, cur_samples, cur_offsets, cur_strand, cur_seq1, cur_seq2 = '', '', '', [], 0, '', '', ''
for line in sys.stdin:
	chrom, start, end, sample, offsets, strand, seq1, seq2 = line.strip().split('\t')[:8]
	if cur_chrom and cur_chrom == chrom and cur_start == start and cur_end == end and cur_strand == strand:
		cur_offsets += int(offsets)
		cur_samples += [sample]
	else:
		if cur_chrom:
			print '\t'.join(map(str, [cur_chrom, cur_start, cur_end, ','.join(cur_samples), cur_offsets, cur_strand, cur_seq1, cur_seq2]))
		cur_chrom, cur_start, cur_end, cur_samples, cur_offsets, cur_strand, cur_seq1, cur_seq2 = chrom, start, end, [sample], int(offsets), strand, seq1, seq2
print '\t'.join(map(str, [cur_chrom, cur_start, cur_end, ','.join(cur_samples), cur_offsets, cur_strand, cur_seq1, cur_seq2]))
