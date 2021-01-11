#!/usr/bin/python3
import argparse
import csv
import math

def readresults(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        result = {}
        for row in reader:
            result[(row[0], row[1])] = {
                    'sizepcnt': float(row[2][:-1]),
                    'time': float(row[3][:-1]),
                }
    return result

def delta(base, eval):
    if base == eval:
        return '=       '
    elif base > eval:
        pcnt = 100 * (1. - eval / base)
        return f'- {pcnt:05.2f}%'
    else:
        pcnt = 100 * (1 - base / eval)
        return f'+ {pcnt:05.2f}%'
    
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-base', required=True)
    ap.add_argument('-eval', required=True)
    args = ap.parse_args()

    br = readresults(args.base)
    er = readresults(args.eval)

    print('| FILE                 | CONFIG               | DEFLATE Δ | TIME Δ    |')
    print('|----------------------|----------------------|-----------|-----------|')
    for itm in sorted(set(br.keys()) | set((er.keys()))):
        (file, config) = itm
        line = f'| {file.ljust(20)} | {config.ljust(20)} | '
        if itm not in br:
            print(line + 'eval only | eval only |')
            continue
        if itm not in er:
            print(line + 'base only | base only |')
            continue
        b = br[itm]
        e = er[itm]
        flatedelta = delta(b['sizepcnt'], e['sizepcnt']) + ' '
        timedelta = delta(b['time'], e['time']) + ' '
        print(line + f'{flatedelta} | {timedelta} |')

