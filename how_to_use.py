import pickle


path = 'bin/wiktionary_obj.p'
with open(path, 'rb') as infile:
    wikt_obj = pickle.load(infile)


print(wikt_obj.wikt_translations[('English', 'dictionary', 'N', 'Dutch')])
print(wikt_obj.wikt_translations[('Dutch', 'woordenboek', 'N', 'English')])
print(wikt_obj.wikt_translations[('English', 'dictionary', 'N', 'Italian')])
