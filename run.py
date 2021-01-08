#!/usr/bin/python3
import argparse
import itertools
import subprocess
import time
import os
import logging

def run(cmd):
    logging.info(f'running "{cmd}"')
    tbeg = time.time()
    out = subprocess.check_output(cmd, shell=True)
    tend = time.time()
    return (out, tend - tbeg)

def runbench(cmd, lvls, wins, files, nruns):
    for file in files:
        results = {}
        for config in itertools.product(lvls, wins):
            (lvl, win) = config
            if lvl < 0:
                lvl = f'-fast={-lvl}'
            elif lvl > 19:
                lvl = f'-ultra -{lvl}'
            config = f'--long={win} -{lvl}'
            results[config] = {'compressed': 0, 'times': []}
            for _ in range(nruns):
                (out, time) = run(f'{cmd} {config} < {file} | wc -c')
                results[config]['compressed'] = int(out)
                results[config]['times'].append(time)
                if time > 20 * 60:
                    # if it runs for too long, don't bother
                    # doing many runs
                    break
        for (config, result) in results.items():
            best = min(result['times'])
            size = os.path.getsize(file)
            pcnt = 100. * float(result['compressed']) / size
            print(f'{file}, `{config}`, {pcnt:.2f}%, {best:.3f}s', flush=True)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-cmd', required=True)
    ap.add_argument('-levels', default='1') #default='1,5,7,16,19,22')
    ap.add_argument('-ldmwin', default='27,30')
    ap.add_argument('-nruns', default=5, type=int)
    ap.add_argument('-bench', default=0, type=int)
    ap.add_argument('-singlethreaded', action='store_true')
    ap.add_argument('-v', action='store_true')
    args = ap.parse_args()

    if args.v:
        logging.basicConfig(level=logging.INFO)

    lvls = [int(l) for l in args.levels.split(',')]
    wins = [int(w) for w in args.ldmwin.split(',')]

    files = ['l5.tar']
    if args.bench > 0:
        files += ['l1m.tar', 'l1y.tar']
    if args.bench > 1:
        files += ['hhvm-rt.tar']
    if args.bench > 2:
        files += ['bkup.tar'] 
    files = ['data/' + f for f in files]

    cmd = args.cmd if args.singlethreaded else f'{args.cmd} -T0'

    runbench(cmd, lvls, wins, files, args.nruns)
