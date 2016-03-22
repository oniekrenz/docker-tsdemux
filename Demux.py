import argparse
import json
import os
import re
import subprocess
import time

ts_pattern = re.compile('^.*\.(\d{4}-\d{2}-\d{2}\.\d{2}-\d{2})\.ts$')
vdr_pattern = re.compile('^(\d{4}-\d{2}-\d{2}\.\d{2}.\d{2})\.\d{2}\.\d{2}\.rec$')

argparser = argparse.ArgumentParser()
argparser.add_argument('jobfile', help='JSON file with demux jobs')
argparser.add_argument('-t', '--test', help='test only, do not demux', action="store_true")
argparser.add_argument('-w', '--watch', help='enter watch mode and wait until the jobfile exists', action="store_true")
args = argparser.parse_args()


def get_jobs(path, title):
    jobs = []
    basename = os.path.basename(path)
    if os.path.isfile(path):
        match = ts_pattern.match(basename)
        if match:
            timestamp = time.strptime(match.group(1), '%Y-%m-%d.%H-%M')
            job = {'title': title, 'files': [path], 'timestamp': timestamp}
            jobs.append(job)
    else:
        match = vdr_pattern.match(basename)
        if match:
            files = [os.path.join(path, file) for file in os.listdir(path) if re.match('\d+\.vdr$', file)]
            files.sort()
            timestamp = time.strptime(match.group(1), '%Y-%m-%d.%H.%M')
            job = {'title': title, 'files': files, 'timestamp': timestamp}
            jobs.append(job)
        else:
            for file in os.listdir(path):
                subdir = os.path.join(path, file)
                jobs.extend(get_jobs(subdir, title))
    return jobs


def create_jobs(job_definition, job_definition_dir):
    rootdir = job_definition['root'] if 'root' in job_definition else job_definition_dir
    jobs = []
    if 'entries' in job_definition:
        for entry in job_definition['entries']:
            entrydir = entry['dir'] if 'dir' in entry else ''
            title = entry['title'] if 'title' in entry else ''
            jobs.extend(get_jobs(os.path.join(rootdir, entrydir), title))
    return jobs


def add_language_to_audio_files(dir, name):
    pids = {}
    log_file_name = os.path.join(dir, name + '_log.txt')
    with open(log_file_name, 'r') as log_file:
        context = 'none'
        pid = ''
        print "reading log " + log_file_name
        for line in log_file:
            pid_match = re.match('^PID: 0x(\w+)\{(\w+)\}.*', line)
            output_match = re.match('^\+\+> .*?: PID 0x(\w+) .*', line)
            if (pid_match):
                pids[pid_match.group(1)] = pid_match.group(2)
            elif output_match:
                context = 'output'
                pid = output_match.group(1)
            elif line == '':
                context = 'none'
            if (context == 'output'):
                out_match = re.match('---> new File: \'(.*?)\'', line)
                if (out_match and pid in pids):
                    lang = pids[pid]
                    new_file = re.sub('(\.\w+)$', ' ' + lang + '\\1', out_match.group(1))
                    print "move " + out_match.group(1) + ' -> ' + new_file
                    os.rename(out_match.group(1), new_file)


def process_jobs(jobs, root_dir):
    dest_dir = root_dir
    for job in jobs:
        name = job['title'] + time.strftime('_%Y-%m-%d_%H-%M', job['timestamp'])
        demux_cmd = ['java', '-jar', '/opt/Project-X_0.91.0/ProjectX.jar']
        demux_cmd.extend(['-out', dest_dir, '-name', name, '-demux'])
        demux_cmd.extend(job['files'])
        if args.test:
            print 'Would execute: ' + ' '.join(demux_cmd)
        else:
            print 'Executing: ' + ' '.join(demux_cmd)
            subprocess.call(demux_cmd)
            add_language_to_audio_files(dest_dir, name)


job_definition_file_name = args.jobfile
with open(job_definition_file_name, 'r') as job_definition_file:
    job_definition = json.load(job_definition_file, 'UTF-8')
    root_dir = os.path.dirname(job_definition_file_name)
    jobs = create_jobs(job_definition, root_dir)
    process_jobs(jobs, root_dir)
