from collections import defaultdict, Counter
from scipy import stats

def map_wikt_pos2fn_pos(wikt_pos):
    """
    map Wiktionary part of speech to FrameNet part of speech
    IMPLEMENTED: noun, verbs, and adjectives

    :param str wikt_pos: a part of speech coming from Wiktionary
    """
    fn_pos = None

    if wikt_pos == 'noun':
        fn_pos = 'N'
    elif wikt_pos == 'verb':
        fn_pos = 'V'
    elif wikt_pos == 'adj':
        fn_pos = 'A'

    return fn_pos

assert map_wikt_pos2fn_pos(wikt_pos='noun') == 'N'
assert map_wikt_pos2fn_pos(wikt_pos='verb') == 'V'
assert map_wikt_pos2fn_pos(wikt_pos='adj') == 'A'
assert map_wikt_pos2fn_pos(wikt_pos='bla') == None



class Wiktionary:


    def __init__(self):
        self.lang_lemma_pos2lemma_pos_obj = {}
        self.lang_lemma_pos2lemma_pos_objs = defaultdict(list)
        self.wikt_translations = {}


    def __str__(self):
        info = []

        lang_distr = Counter([lemma_pos_obj.lang
                              for lemma_pos_obj in self.lang_lemma_pos2lemma_pos_obj.values()])
        info.append(f'language distribution lemma pos: {lang_distr}')

        for lang in lang_distr:
            senses_distr = []
            for lemma_pos_obj in self.lang_lemma_pos2lemma_pos_obj.values():
                if lemma_pos_obj.lang == lang:
                    senses_distr.append(len(lemma_pos_obj.senses))

            info.append(' ')
            info.append(f'information about number of senses for {lang}')
            info.append(f'{stats.describe(senses_distr)}')


            lang2translation_distr = defaultdict(list)
            for (src, lemma, pos, target), translations in self.wikt_translations.items():
                if src == lang:
                    lang2translation_distr[target].append(len(translations))

            for target_lang, translation_distr in lang2translation_distr.items():
                info.append(' ')
                info.append(f'information about translations from {lang} to {target_lang}')
                info.append(f'{stats.describe(translation_distr)}')

        return '\n'.join(info)

    def merge_lemma_objs(self):
        """
        there are many duplicates in the Wiktionary extractor
        we choose the page with the highest number of senses
        """
        for key, lemma_objs in self.lang_lemma_pos2lemma_pos_objs.items():
            if len(lemma_objs) == 1:
                chosen_lemma_obj = lemma_objs[0]
            else:
                max_num_senses = -1
                chosen_lemma_obj = None
                for lemma_obj in lemma_objs:
                    num_senses = len(lemma_obj.senses)
                    if num_senses > max_num_senses:
                        chosen_lemma_obj = lemma_obj
                        max_num_senses = num_senses

            self.lang_lemma_pos2lemma_pos_obj[key] = chosen_lemma_obj

    def create_translation_dict(self):
        """
        we assume that there only exist translations from
        English -> other language

        for each translation from English -> target language,
        we store both source -> target and target -> source

        """
        src_lang_lemma_fnpos_target_lang2translations = defaultdict(set)

        for lemma_obj in self.lang_lemma_pos2lemma_pos_obj.values():

            src_lang = lemma_obj.lang
            src_lemma = lemma_obj.lemma
            src_fn_pos = lemma_obj.fn_pos

            for translation_obj in lemma_obj.translations:
                target_lang = translation_obj.lang
                target_lemma = translation_obj.lemma
                target_fnpos = translation_obj.fn_pos

                # from English to other language
                key = (src_lang, src_lemma, src_fn_pos, target_lang)
                value = (target_lemma, target_fnpos)
                src_lang_lemma_fnpos_target_lang2translations[key].add(value)

                # from other language to English
                key = (target_lang, target_lemma, target_fnpos, src_lang)
                value = (src_lemma, src_fn_pos)
                src_lang_lemma_fnpos_target_lang2translations[key].add(value)


        self.wikt_translations = src_lang_lemma_fnpos_target_lang2translations








class LemmaPos:

    def __init__(self,
                 namespace,
                 short_namespace,
                 lang,
                 lemma,
                 wikt_pos,
                 fn_pos):
        self.namespace = namespace
        self.short_namespace = short_namespace
        self.lang = lang
        self.lemma = lemma
        self.wikt_pos = wikt_pos
        self.fn_pos = fn_pos
        self.senses = []
        self.translations = []

    def set_sense_ranks(self):
        for sense_rank, sense_obj in enumerate(self.senses, 1):
            sense_obj.sense_rank = sense_rank

    def __str__(self):
        info = [' ', f'LEMMA-POS: {self.get_short_rdf_uri()} ({self.get_full_rdf_uri()})']
        for attr in ['lang', 'lemma', 'fn_pos']:
            info.append(f'attribute {attr}: {getattr(self, attr)}')

        for sense_obj in self.senses:
            info.append(' ')
            info.append(sense_obj.__str__())

        for translation_obj in self.translations:
            info.append(translation_obj.__str__())

        return '\n'.join(info)

    def get_full_rdf_uri(self):
        return f'{self.namespace}{self.lemma}#{self.wikt_pos.title()}'

    def get_short_rdf_uri(self):
        return f'{self.short_namespace}:{self.lemma}#{self.wikt_pos.title()}'

class Sense:

    def __init__(self,
                 namespace,
                 short_namespace,
                 lang,
                 lemma,
                 wikt_pos,
                 fn_pos,
                 glosses,
                 idiomatic):
        self.namespace = namespace
        self.short_namespace = short_namespace
        self.lang = lang
        self.lemma = lemma
        self.wikt_pos = wikt_pos
        self.fn_pos = fn_pos
        self.glosses = glosses
        self.idiomatic = idiomatic
        self.sense_rank = None

    def __str__(self):
        info = [f'SENSE: {self.get_short_rdf_uri()}']
        for attr in ['lang', 'lemma', 'fn_pos', 'sense_rank', 'idiomatic', 'glosses']:
            info.append(f'{attr}: {getattr(self, attr)}')

        return '\n'.join(info)

    def get_full_rdf_uri(self):
        return f'{self.namespace}{self.lemma}#{self.wikt_pos.title()}'

    def get_short_rdf_uri(self):
        return f'{self.short_namespace}:{self.lemma}#{self.wikt_pos.title()}-{self.sense_rank}'


class Translation:


    def __init__(self, lang, lemma, wikt_pos, fn_pos, translation_id, gloss):
        self.lang = lang
        self.lemma = lemma
        self.wikt_pos = wikt_pos
        self.fn_pos = fn_pos
        self.translation_id = translation_id
        self.gloss = gloss

    def __str__(self):
        info = [' ', f'TRANSLATION: {self.translation_id}']
        for attr in ['lang', 'lemma', 'fn_pos', 'gloss']:
            info.append(f'{attr}: {getattr(self, attr)}')

        return '\n'.join(info)

