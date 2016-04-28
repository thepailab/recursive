import sys
import matplotlib.pyplot as plt
WINDOWS = 100


def increased(peak, expression):
    WIDTH = 100
    before = sum(expression[peak - WIDTH: peak])
    after = sum(expression[peak:peak + WIDTH])

    return after > 2 * before


def get_peaks(probs, z):
    WIDTH = 5
    peaks = []
    avg = sum(probs) / float(len(probs))
    for i in xrange(WIDTH, len(probs)-WIDTH):
        if probs[i] / z < .1: continue
        if all(probs[i-j] < probs[i] and probs[i] > probs[i+j] for j in range(1, WIDTH)):
            peaks += [i]
    return peaks


def get_probs(samples, expression):
    length = (len(expression) / WINDOWS) + 1
    counts = [0] * length
    for sample in samples:
        for ratchet in sample:
            counts[ratchet] += 1
    max_expression = max(expression)
    for i in xrange(len(counts)):
        counts[i] = (counts[i] * max_expression) / float(len(samples))
    return counts

def get_prob(pos, start, mcmc, z):
    window = abs(pos - start) / WINDOWS
    score = 0
    for i in range(-5, 10):
        try:
            score = max(score, mcmc[window + i])
        except IndexError: pass
    return score / float(z)

graveley = open('../data/graveley.bed', 'r')

grav = []
for line in graveley:
    chrom, start, end, name, score, strand = line.strip().split('\t')
    if strand == '+':
        grav += [(chrom, strand, int(end))]
    else:
        grav += [(chrom, strand, int(start))]

novel = open('../data/all_plus_total.bed', 'r')

nov = []
for line in novel:
    chrom, start, end, name, score, strand, seq1, seq2 = line.strip().split('\t')

    if seq1[-2:] != 'AG' or seq2[:2] != 'GT': continue
    if strand == '+':
        nov += [(chrom, strand, int(end))]
    else:
        nov += [(chrom, strand, int(start))]



data = open(sys.argv[1], 'r')
c = 0
y, n = 0,0
for line in data:
    c += 1
    #print c
    #if c < 200: continue 
    chrom, start, end, offsets, rs, strand = line.strip().split('\t')[:6]
    expression = [int(i) for i in line.strip().split('\t')[-2].split(",")]
    mcmc = [float(i) for i in line.strip().split('\t')[-1].split(",")]
    
    if line.split('\t')[5] == "-":
        expression.reverse()

    peaks = get_peaks(mcmc, max(expression))

    # for peak in peaks:
    #     if increased(peak * WINDOWS, expression):
    #         plt.axvline(peak * WINDOWS, linewidth=3, color='r')
    #     else:
    #         plt.axvline(peak * WINDOWS, linewidth=3, color='m')

    missed = False
    for gchrom, gstrand, grs in grav:
        if gchrom == chrom and gstrand == strand and int(start) < grs < int(end):
            if strand == '+':
                p = get_prob(grs, int(start), mcmc, max(expression))
                pos = grs - int(start)
#                plt.axvline(int(grs) - int(start), linewidth=4, color='g')
            elif strand == '-':
                p = get_prob(grs, int(end), mcmc, max(expression))
                pos = int(end) - grs
#                plt.axvline(int(end) - int(grs), linewidth=4, color='g')
            if p > .1:
                y += 1
            else:
                n += 1
                missed = True
            # inside = False
            # for peak in peaks:
            #     if (peak - 2) * WINDOWS < pos < (peak+2) * WINDOWS:
            #         inside = True
            # print p, inside
            # missed = missed or (not inside)


    

    # chrom, start, end, offsets, rs, strand = line.strip().split('\t')[:6]

    # for offset, ratchet in zip(offsets.split(','), rs.split(',')):
    #     if len(offset) > 3 and offset[:4] == 'grav':
    #         if len(offset) > 4:
    #             count = int(offset[4:])
    #         else:
    #             count = 0
    #         if strand == '+':
    #             plt.axvline(int(ratchet) - int(start), linewidth=4, color='g')
    #         elif strand == '-':
    #             plt.axvline(int(end) - int(ratchet), linewidth=4, color='g')
    #     else:
    #         count = int(offset)

    #     if count:
    #         if strand == '+':
    #             plt.axvline(int(ratchet) - int(start), linewidth=2, color='r')
    #         elif strand == '-':
    #             plt.axvline(int(end) - int(ratchet), linewidth=2, color='r')

    if missed or True:
        print chrom, start, end, strand
        for gchrom, gstrand, grs in grav:
            if gchrom == chrom and gstrand == strand and int(start) < grs < int(end):
                if strand == '+':
                    pos = grs - int(start)
                elif strand == '-':
                    pos = int(end) - grs
                plt.axvline(pos, linewidth=4, color='g')

        # for peak in peaks:
        #     if increased(peak * WINDOWS, expression):
        #         plt.axvline(peak * WINDOWS, linewidth=2, color='r')
        #     else:
        #         plt.axvline(peak * WINDOWS, linewidth=2, color='m')

        for gchrom, gstrand, grs in nov:
            if gchrom == chrom and gstrand == strand and int(start) < grs < int(end):
                if strand == '+':
                    pos = grs - int(start)
                elif strand == '-':
                    pos = int(end) - grs
                plt.axvline(pos, linewidth=2, color='r')


        x = range(0, len(expression), WINDOWS)
        if len(mcmc) != len(x): x = range(0, len(expression)+1, WINDOWS)
        plt.plot(x, mcmc, linewidth=6, color= 'k')

        plt.plot(expression)
        plt.show(block = False)
        a = raw_input("enter to continue")
        plt.close()
print y, n
