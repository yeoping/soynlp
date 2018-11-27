from collections import namedtuple
from soynlp.hangle import character_is_complete_korean
from soynlp.lemmatizer import Lemmatizer
from soynlp.lemmatizer import lemma_candidate
from soynlp.normalizer import remove_doublespace

class Eojeol(namedtuple('Eojeol', 'w0 w1 t0 t1 b m e')):
    def __str__(self):
        if self.w1:
            return '%s/%s + %s/%s' % (self.w0, self.t0, self.w1, self.t1)
        else:
            return '%s/%s' % (self.w0, self.t0)
    def __repr__(self):
        return '[%d, %d, %s/%s + %s/%s]' % (
            self.b, self.e, self.w0, self.t0, self.w1, self.t1)


class LRLookup:
    def __init__(self, pos_to_words, max_word_len=0):
        self.pos_to_words = pos_to_words
        self.max_word_len = max_word_len
        self.formal_text = True
        self.lemmatizer = self._set_lemmatizer()
        if max_word_len == 0:
            self._check_max_word_len()

    def __call__(self, sentence):
        return self._sentence_lookup(sentence)

    def _check_max_word_len(self):
        if not self.pos_to_words:
            raise ValueError('pos_to_words should not be empty')
        self.max_word_len = max(
            max(len(word) for word in words)
            for words in self.pos_to_words.values()
        )

    def _set_lemmatizer(self):
        lemmatizer = Lemmatizer(
            self.pos_to_words['Adjective'],
            self.pos_to_words['Verb'],
            self.pos_to_words['Eomi'],
            formal_text = self.formal_text
        )
        return lemmatizer

    def _sentence_lookup(self, sentence):
        sentence = remove_doublespace(sentence)
        sent = []
        for eojeol in sentence.split():
            sent += self._eojeol_lookup(eojeol, len(sent))
        return sent

    def _eojeol_lookup(self, eojeol, offset):
        return lr_lookup(eojeol, self.lemmatizer,
            self.pos_to_words, offset)


class TemplateLookup(LRLookup):
    def __init__(self, pos_to_words, templates=None, formal_text=False):
        self.formal_text = formal_text
        super().__init__(pos_to_words)
        if templates is None:
            templates = [
                ('Noun',),
                ('Pronoun',),
                ('Adverb', ),
                ('Exclamation',),
                ('Noun', 'Josa'),
                ('Pronoun', 'Josa'),
                ('Adverb', 'Josa')
            ]
        self.set_templates(templates)

    def append_templates(self, template):
        if isinstance(template, str):
            template = [(template,)]
        templates = [t for t in self.templates] + template
        self.set_templates(templates)

    def set_templates(self, templates):
        templates = self._template_format_check(templates)
        self.templates = templates

    def _template_format_check(self, templates):
        for t in templates:
            if len(t) > 2:
                message = ''.join(('Template length should be less than 2',
                    '{} has {} words'.format(t, len(t))))
                raise ValueError(message)
        return sorted(set(templates), key=lambda x:len(x))

    def _eojeol_lookup(self, eojeol, offset):
        return template_lookup(eojeol, self.lemmatizer,
            self.pos_to_words, self.templates,
            self.max_word_len, offset)

def lr_lookup(eojeol, lemmatizer, dic, offset=0):
    n = len(eojeol)
    bindex = [[] for _ in range(n)]

    # Adjective or Verb
    predicators = lemmatize(eojeol, lemmatizer, offset)
    bindex[0] = predicators

    for i in range(1, n+1):
        l = eojeol[:i]
        r = eojeol[i:]

        # Noun + Josa
        if check_tag(l, 'Noun', dic) and check_tag(r, 'Josa', dic):
            bindex[0].append(
                Eojeol(l, r, 'Noun', 'Josa', offset, offset+i, offset+n)
            )

        l_pred = lemmatize(l, lemmatizer, offset)
        r_pred = lemmatize(r, lemmatizer, offset+i)

        # Noun / Adjective / Verb + Adjective / Verb
        if (check_tag(l, 'Noun', dic) or l_pred) and r_pred:
            if check_tag(l, 'Noun', dic):
                bindex[0].append(
                    Eojeol(l, '', 'Noun', None, offset, offset+i, offset+i)
                )
            else:
                bindex[0] += l_pred
            bindex[i] += r_pred
    return bindex

def template_lookup(eojeol, lemmatizer, dic, templates, max_len, offset=0):
    n = len(eojeol)

    # string match
    bindex = [[] for _ in range(n)]
    predicators = set()
    for b in range(n):
        for e in range(b+1, min(b+max_len, n)+1):
            sub = eojeol[b:e]
            predicators.update(lemmatize(sub, lemmatizer, offset+b))
            for tag in get_tag(sub, dic):
                bindex[b].append((sub, tag, b, e))

    # as Eojeol
    bindex_ = [[] for _ in range(n)]
    for morphs in bindex:
        for w0, t0, b, e in morphs:
            for t in templates:                
                if len(t) == 1 and t0 == t[0]:
                    bindex_[b].append(
                        Eojeol(w0, '', t0, None, offset+b, offset+e, offset+e)
                    )
                elif e < n and len(t) == 2 and t0 == t[0]:
                    for w1, t1, m, e_ in bindex[e]:
                        if t1 == t[1]:
                            bindex_[b].append(
                                Eojeol(w0, w1, t0, t1, offset+b, offset+m, offset+e_)
                            )

    # remove overlapped subwords
    bindex_ = remove_sub(bindex_, offset)

    # add predicators
    for word in predicators:
        bindex_[word.b-offset].append(word)

    return bindex_

def remove_sub(bindex, offset=0):
    def exist_overlap_l(b, e, bindex):
        for i in range(b, e):
            for eojeol in bindex[i-offset]:
                if (b < eojeol.m) and (eojeol.b < e):
                    return True
        return False

    def skip(eojeol, bm_pair, me_pair):
        for b, m, t in bm_pair:
            if (not eojeol.w1) and (eojeol.b == b) and (eojeol.m == m) and (eojeol.t0 == t):
                return True
        for m, e, t in me_pair:
            if (eojeol.w1) and (eojeol.m == m) and (eojeol.e < e) and (eojeol.t1 == t):
                return True
        return False

    for b, eojeols in enumerate(bindex):
        bm_pair = set()
        me_pair = set()
        for eojeol in eojeols:
            r_b = eojeol.m
            r_e = eojeol.e
            if eojeol.w1 and not exist_overlap_l(r_b, r_e, bindex):
                bm_pair.add((eojeol.b, r_b, eojeol.t0))
                me_pair.add((r_b, r_e, eojeol.t1))

        eojeols_ = []
        for eojeol in eojeols:
            if skip(eojeol, bm_pair, me_pair):
                continue
            eojeols_.append(eojeol)

        bindex[b] = eojeols_
    return bindex

def lemmatize(word, lemmatizer, offset=0, ensure_hangle=False):
    def is_hangle(word):
        for c in word:
            if not character_is_complete_korean(c):
                return False
        return True

    morphs = []
    if not ensure_hangle and not is_hangle(word):
        return []

    for w0, w1, t0, t1 in lemmatizer.lemmatize(word):
        morphs.append(
            Eojeol(w0, w1, t0, t1, offset, offset+len(w0), offset+len(word))
        )
    return morphs

def check_tag(word, tag, pos_to_words):
    return word in pos_to_words.get(tag, {})

def get_tag(word, pos_to_words):
    return tuple(tag for tag, words in pos_to_words.items() if word in words)