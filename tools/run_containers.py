#!/usr/bin/env python3
import sys
import os
import argparse
import queue
import subprocess as sp
from multiprocessing import Lock, Process, Queue, current_process


printlock = Lock()

def file_exists(path):
    """Check if file exists and is not empty"""
    return os.path.isfile(path) and os.path.getsize(path) > 0


def detect_report(volume, package):
    try:
        a = os.walk(volume + '/' + package)
        next(a)
        next(a)
        dirname, _, filenames = next(a)
        if 'report' in filenames:
            with open(dirname + '/report') as fp:
                for line in fp:
                    if 'fcan' in line and 'success' in line:
                        return True
                return False
    except Exception as exc:
        return False


def mprint(ptype, pname, message, sname):
    with printlock:
        print("{}-{}: {}: {}".format(ptype, pname, message, sname))
        sys.stdout.flush()


# Task should be a function
def do_work(in_queue, tq, fq, sq, volume, docker_image, timeout, release,
            architecture):
    while True:
        try:
            val = in_queue.get_nowait()
        except queue.Empty:
            break
        else:
            # Run docker image and detect if .straces
            mprint(docker_image, current_process().name, "consumed", val)
            docker_options = [
                'docker',
                'run',
                '--rm',
                '--privileged',
                '-v',
                volume + ':/callgraphs',
                docker_image,
                'sbuild',
                '--apt-update',
                '--no-apt-upgrade',
                '--no-apt-distupgrade',
                '--batch',
                '--stats-dir=/var/log/sbuild/stats',
                '--dist=' + release,
                '--arch=' + architecture,
                val
            ]
            try:
                sp.run(
                    docker_options, stdout=sp.PIPE, stderr=sp.PIPE,
                    timeout=timeout
                )
            except sp.TimeoutExpired as exc:
                tq.put(val)
                mprint(docker_image, current_process().name, "timeout", val)
                continue
            except Exception as exc:
                fq.put(val)
                mprint(docker_image, current_process().name, "exception", val)
                continue
            if detect_report(volume, val):
                sq.put(val)
                mprint(docker_image, current_process().name, "success", val)
            else:
                fq.put(val)
                mprint(docker_image, current_process().name, "failed", val)
    return True


def main(inp, volume, pn, docker_image, timeout, release, architecture):
    number_of_processes = pn
    # Elements: source_name
    q = Queue() # sources
    tq = Queue() # timeout queue
    fq = Queue() # failed queue
    sq = Queue() # success queue
    processes = []

    for i in inp:
        q.put(i.strip())

    # creating processes
    for _ in range(number_of_processes):
        p = Process(
            target=do_work,
            args=(q, tq, fq, sq, volume, docker_image, timeout, release,
                  architecture
                 )
        )
        processes.append(p)
        p.start()

    # completing process
    for p in processes:
        p.join()

    # print results
    print("###TIMEOUT###")
    while not tq.empty():
        print(tq.get())
    print("###FAILED###")
    while not fq.empty():
        print(fq.get())
    print("###SUCCESS###")
    while not sq.empty():
        print(sq.get())

    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input',
                        help='Give a file to read projects name'
                       )
    parser.add_argument('-r', '--release', default='buster')
    parser.add_argument('-a', '--architecture', default='amd64')
    parser.add_argument('-t', '--timeout', type=int, default=1800)
    parser.add_argument('volume_dir')
    parser.add_argument('docker_image')
    parser.add_argument('processes', type=int)
    args = parser.parse_args()
    inp = sys.stdin
    if args.input:
        with open(args.input, 'r') as f:
            inp = f.readlines()
    main(
        inp,
        args.volume_dir,
        args.processes,
        args.docker_image,
        args.timeout,
        args.release,
        args.architecture
    )
