"""
02 Dec 2012

global aligner for Topologically Associated Domains
"""


def needleman_wunsch(tads1, tads2, bin_size=None, penalty=-0.1,
                     max_dist=500000, verbose=False):
    """
    Align two lists of TAD's boundaries.
    
    :param tads1: list of boundaries for one chromosome under one condition
    :param tads2: list of boundaries for the same chromosome under other
        conditions
    :param None bin_size: resolution at which TADs are predicted in number of
        bases. Default is 1
    :param None chr_len: length of input chromosome. Default set to the maximum
        value of tads1 and tads2.
    :param -0.1 penalty: penalty to open a gap in the alignment of boundaries
    :param 500000 max_dist: distance from which match are denied. A bin_size
        of 20Kb the number of bins corresponding to 0.5Mb is 25.
    :param False verbose: print the Needleman-Wunsch score matrix, and the
        alignment of boundaries

    :returns: the max score in the Needleman-Wunsch score matrix.
    """
    ##############
    tads1 = [0.0] + tads1
    tads2 = [0.0] + tads2
    l_tads1  = len(tads1)
    l_tads2  = len(tads2)
    bin_size = bin_size or 1
    dister = lambda x, y: 10000. / (bin_size * (abs(x - y) + 1))
    scores = virgin_score(penalty, l_tads1, l_tads2)
    for i in xrange(1, l_tads1):
        for j in xrange(1, l_tads2):
            d_dist = dister(tads2[j], tads1[i])
            match  = d_dist + scores[i-1][j-1]
            insert = scores[i-1][j] + penalty
            delete = scores[i][j-1] + penalty
            if d_dist > max_dist:
                scores[i][j] = max((insert, delete))
            else:
                scores[i][j] = max((match, insert, delete))
    align1 = []
    align2 = []
    i = l_tads1 -1
    j = l_tads2 -1
    max_score = None
    while i and j:
        score      = scores[i][j]
        if score > max_score:
            if i and j:
                max_score = score
        d_dist     = dister(tads2[j], tads1[i])
        value      = scores[i-1][j-1] + d_dist
        if equal(score, value):
            align1.insert(0, tads1[i])
            align2.insert(0, tads2[j])
            i -= 1
            j -= 1
        elif equal(score, scores[i-1][j] + penalty):
            align1.insert(0, tads1[i])
            align2.insert(0, '-')
            i -= 1
        elif equal(score, scores[i][j-1] + penalty):
            align1.insert(0, '-')
            align2.insert(0, tads2[j])
            j -= 1
        else:
            for scr in scores: 
                print ' '.join(['%6s' % (round(y, 2)) for y in scr])
            raise Exception('Something  is failing and it is my fault...',
                            i, j, tads1[i], tads2[j])
    if verbose:
        print '\n Alignment:'
        print 'TADS 1: '+'|'.join(['%4s' % (str(int(x)) if x!='-' else '-'*3) \
                                   for x in align1])
        print 'TADS 2: '+'|'.join(['%4s' % (str(int(x)) if x!='-' else '-'*3) \
                                   for x in align2])
    return [align1, align2], max_score


def virgin_score(penalty, l_tads1, l_tads2):
    zeros    = [0.0 for _ in xrange(l_tads2)]
    return [[penalty * j for j in xrange(l_tads2)]] + \
           [[penalty * i] + zeros for i in xrange(1, l_tads1)]


def equal(a, b, cut_off=1e-9):
    return abs(a-b) < cut_off
