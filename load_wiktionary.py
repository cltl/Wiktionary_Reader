"""
Load Wiktionary information from multiple languages into classes.Wiktionary object

Usage:
  load_wiktionary.py --config_path=<config_path> --min_num_senses=<min_num_senses>\
  --output_folder=<output_folder> --verbose=<verbose>

Options:
    --config_path=<config_path> see example 'config/en_it_du.json'
    --min_num_senses=<min_num_senses> each word needs minimally x number of senses (can be 0)
    --output_folder=<output_folder>
    --verbose=<verbose> 0 --> no stdout 1 --> general stdout 2 --> detailed stdout

Example:
    python load_wiktionary.py --config_path="config/en_it_du.json" --min_num_senses="1" --output_folder="bin" --verbose="2"
"""
import json
import pickle
from shutil import rmtree
from pathlib import Path
from docopt import docopt

from wiktionary_classes import Wiktionary, LemmaPos, Sense, Translation, map_wikt_pos2fn_pos

# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

out_folder = Path(arguments['--output_folder'])
if out_folder.exists():
    rmtree(str(out_folder))
out_folder.mkdir()
output_path = out_folder / 'wiktionary_obj.p'
verbose= int(arguments['--verbose'])
min_num_senses = int(arguments['--min_num_senses'])

settings = json.load(open(arguments['--config_path']))
language2info = settings['language2info']
translation_languages = settings['translation_languages']

# loop data
wikt_obj = Wiktionary()


with open(settings['wikt_words_path']) as infile:
    for line in infile:
        info = json.loads(line)


        # check lemma
        lemma = info['word']

        # check language
        if 'lang' not in info:  # mostly redirects
            if verbose >= 3:
                print('lemma has no language')
            continue

        lang = info['lang']
        if lang not in language2info:
            if verbose >= 3:
                print(f'skipping {lemma} with lang: {lang}')
            continue

        source_lang = lang
        namespace = language2info[source_lang]['namespace']
        short_namespace = language2info[source_lang]['short_namespace']

        # check pos
        wikt_pos = info['pos']
        fn_pos = map_wikt_pos2fn_pos(wikt_pos)

        if fn_pos is None:
            if verbose >= 3:
                print(f'skipping lemma with pos: {wikt_pos}')
            continue

        key = (source_lang, lemma, fn_pos)
        lemma_obj = LemmaPos(namespace, short_namespace, lang, lemma, wikt_pos, fn_pos)

        # senses
        if 'senses' in info:
            for sense_info in info['senses']:
                if 'glosses' in sense_info:
                    idiomatic = False
                    if 'tags' in sense_info:
                        if 'idiomatic' in sense_info['tags']:
                            idiomatic = True

                    sense_obj = Sense(namespace,
                                      short_namespace,
                                      lang,
                                      lemma,
                                      wikt_pos,
                                      fn_pos,
                                      glosses=sense_info['glosses'],
                                      idiomatic=idiomatic)

                    lemma_obj.senses.append(sense_obj)

        lemma_obj.set_sense_ranks()

        # translations
        if 'translations' in info:
            for translation_info in info['translations']:
                target_lang = translation_info['lang']
                if 'sense' in translation_info:
                    if target_lang in translation_languages:
                        target_lang = translation_languages[target_lang]
                        target_lemma = translation_info['word']
                        target_namespace = language2info[target_lang]['namespace']
                        translation_id = f'{target_namespace}{target_lemma}#{wikt_pos.title()}'

                        translation_obj = Translation(lang=target_lang,
                                                      lemma=target_lemma,
                                                      wikt_pos=wikt_pos,
                                                      fn_pos=fn_pos,
                                                      translation_id=translation_id,
                                                      gloss=translation_info['sense'])

                        lemma_obj.translations.append(translation_obj)



        if len(lemma_obj.senses) >= min_num_senses:
            wikt_obj.lang_lemma_pos2lemma_pos_objs[key].append(lemma_obj)
        else:
            if verbose >= 3:
                print()
                print(f'NOT ENOUGH SENSES:')
                print(lemma_obj)
                input('continue?')


wikt_obj.merge_lemma_objs()
wikt_obj.create_translation_dict()

if verbose >= 1:
    print(wikt_obj)

with open(str(output_path), 'wb') as outfile:
    if verbose >= 1:
        print(f'writing output to {output_path}')
    pickle.dump(wikt_obj, outfile)
