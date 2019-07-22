#!/usr/bin/env bash
wiktwords resources/enwiktionary-latest-pages-articles.xml.bz2 --out output/wikt.en_du_it.words --language English --language Dutch --language Italian --translations  > output/log.out 2> output/log.err &

