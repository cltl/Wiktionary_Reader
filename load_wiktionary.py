"""
Load Wiktionary information from multiple languages into classes.Wiktionary object

Usage:
  load_wiktionary.py --config_path=<config_path> --output_folder=<output_folder> --verbose=<verbose>

Options:
    --config_path=<config_path> see example 'config/en_it_du.json'
    --output_folder=<output_folder>
    --verbose=<verbose> 0 --> no stdout 1 --> general stdout 2 --> detailed stdout

Example:
    python load_wiktionary.py --config_path="config/en_it_du.json" --output_folder="bin" --verbose="2"
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

settings = json.load(open(arguments['--config_path']))
loop_info = settings['paths_info']
language2info = settings['language2info']
translation_languages = settings['translation_languages']

# loop data
wikt_obj = Wiktionary()

for source_lang, path in loop_info.items():
    namespace = language2info[source_lang]['namespace']
    short_namespace = language2info[source_lang]['short_namespace']

    with open(path) as infile:
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
            if lang != source_lang:
                if verbose >= 3:
                    print(f'skipping {lemma} with lang: {lang}')
                continue

            # check pos
            wikt_pos = info['pos']
            fn_pos = map_wikt_pos2fn_pos(wikt_pos)

            if fn_pos is None:
                if verbose >= 3:
                    print(f'skipping lemma with pos: {wikt_pos}')
                continue

            key = (source_lang, lemma, fn_pos)
            lemma_obj = LemmaPos(namespace, short_namespace, lang, lemma, wikt_pos, fn_pos)
            wikt_obj.lang_lemma_pos2lemma_pos_objs[key].append(lemma_obj)

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

wikt_obj.merge_lemma_objs()
wikt_obj.create_translation_dict()

if verbose >= 1:
    print(wikt_obj)

with open(str(output_path), 'wb') as outfile:
    if verbose >= 1:
        print(f'writing output to {output_path}')
    pickle.dump(wikt_obj, outfile)