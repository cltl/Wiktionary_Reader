#!/usr/bin/env bash

rm -rf output
mkdir output

rm -rf resources
mkdir resources
cd resources

wget https://dumps.wikimedia.org/enwiktionary/latest/enwiktionary-latest-pages-articles.xml.bz2
