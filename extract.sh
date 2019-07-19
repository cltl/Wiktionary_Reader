#!/usr/bin/env bash
wiktwords resources/enwiktionary-latest-pages-articles.xml.bz2 --out output/wikt.english.words --language English --all --translations --linkages --compounds
wiktwords resources/enwiktionary-latest-pages-articles.xml.bz2 --out output/wikt.dutch.words --language Dutch --all --translations --linkages --compounds
wiktwords resources/enwiktionary-latest-pages-articles.xml.bz2 --out output/wikt.italian.words --language Italian --all --translations --linkages --compounds

