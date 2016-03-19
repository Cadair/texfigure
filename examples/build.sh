#!/bin/bash

pdflatex -shell-escape -interaction=batchmode $1
pythontex $1
pdflatex -shell-escape -interaction=batchmode $1
