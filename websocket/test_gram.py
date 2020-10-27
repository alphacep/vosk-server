#!/usr/bin/env python3

import os
import sys
import pathlib
import random
import re

def readFile(path: str) -> tuple:
    read_data = []
    with open(path, "r") as f:
        read_data = f.readlines()
    return read_data

def parseGram(grammar: tuple) -> dict:
    gramdata = {}
    publicgrams = {}
    for line in grammar:
        line = line.strip()
        if line.startswith('<') and line.find('=') != -1  and line.find(';') != -1:
            key = line[1:line.index('>')]
            value = line[line.index('=')+1:line.index(';')].strip()
            value = value.replace('*', '.*')
#            value = value.replace(')', '){1}')
            value = value.replace('[', '(')
            value = value.replace(']', '){0,1}')
            start = 0
            while(value.find('<', start)!=-1 and value.index('>', start)!=-1):
                gram = value[value.index('<', start)+1:value.index('>', start)].strip()
                gramregexp = gramdata.pop(gram)
                start = value.index('<', start)
                value = value.replace(value[start:value.index('>', start)+1], '(' + gramregexp + ')')
                start += len(gramregexp)+1
            value = value.strip()
            if value[-1] == '|':
                value = value[0:-1]
            value = value.replace('(', '(<')
            value = value.replace(')', '>)')
            value = value.replace(' ', '><')
            value = value.replace(')>', ')')
            value = value.replace('<|', '|')
            value = value.replace('|>', '|')
            value = value.replace('<(', '(')
            value = value.replace('}>', '}')
            value = value.replace('<<', '<')
            value = value.replace('>>', '>')
            if not value[0] in ['(', '<']:
                value = '<' + value
            if not value[-1] in [')', '}', '>']:
                value = value + '>'
            value = value.replace('<', '\\s*\\b')
            value = value.replace('>', '\\b\\s*')
            value = value.replace('\\b\\b', '\\b')
            value = value.replace('\\b\\s*\\b', '\\b')
            gramdata[key] = value
        if line.startswith('public ') and line.find('=') != -1  and line.find(';') != -1:
            key = line[line.index('<')+1:line.index('>')]
            value = line[line.index('=')+1:line.index(';')].strip()
            grams = []
            while(value.find('<')!=-1 and value.index('>')!=-1):
                gram = value[value.index('<')+1:value.index('>')].strip()
                grams.append(gram)
                value = value.replace(value[value.index('<'):value.index('>')+1], '')               
            publicgrams[key] = grams
    return gramdata, publicgrams

def testPhrase(phrase: str, grams: dict, validgrams: tuple):
    matchedgram = 'unknown'
    for gram in validgrams:
        pattern = re.compile(grams[gram])
        if pattern.search(phrase):
            matchedgram = gram
            break
    return matchedgram

phrases = ['соединение установлено пожалуйста подождите', 'я вас слушаю внимательно', 'по какой рекламе']

file = readFile(str(pathlib.Path(__file__).parent.absolute().joinpath('test.gram')))
grams, publicgrams = parseGram(file)

phrase = phrases[random.randint(0, len(phrases)-1)]


print('Test pharse '+phrase)
for variant in publicgrams:
    print('Variant '+variant+': '+testPhrase(phrase, grams, publicgrams[variant]))
