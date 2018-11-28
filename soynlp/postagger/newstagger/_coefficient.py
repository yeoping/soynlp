def to_adjacent_tree(bindex):
    def useful(eojeol):
        if eojeol.t0 == 'Adjective':
            return True
        elif eojeol.t0 == 'Verb':
            return True
        elif (eojeol.t0 == 'Noun') and (eojeol.b+1 < eojeol.m):
            return True
        else:
            return eojeol.t0 == 'Adverb'

    def parse(eojeol):
        return (eojeol.w0, eojeol.t0)

    def select(eojeols):
        return list({parse(eojeol) for eojeol in eojeols if useful(eojeol)})

    def adjacent_index(b, n):
        for i in range(b, n):
            if bindex_[i]:
                return i
        return i

    n = len(bindex)
    max_i = n - 1
    bindex_ = [select(eojeols) for eojeols in bindex]
    tree = {}

    for b, eojeols in enumerate(bindex_):
        for eojeol in eojeols:
            adj_idx = adjacent_index(b + len(eojeol[0]), n)
            if adj_idx == max_i:
                continue
            tree[eojeol] = bindex_[adj_idx]
    return tree

def cooccurrence(sents):
    def to_dict(dd):
        return {base:dict(d) for base, d in dd.items()}

    ddp = defaultdict(lambda: defaultdict(int)) # previous
    ddf = defaultdict(lambda: defaultdict(int)) # following
    for i, sent in enumerate(sents):
        bindex = lookup_buffer(sent)
        tree = to_adjacent_tree(bindex)
        for base, adjacents in tree.items():
            for adj in adjacents:
                ddf[base][adj] += 1
                ddp[adj][base] += 1
    return to_dict(ddp), to_dict(ddf)