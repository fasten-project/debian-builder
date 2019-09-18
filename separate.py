"""
Separate a make.cs file two multiple per project.
"""
import sys
import os


DIRECTORY = 'cscout_files'


def can_project(project):
    if not project.find('/'):
        project = project.replace('/', '__')
    return '{}/{}.cs'.format(DIRECTORY, project)


if len(sys.argv) != 2:
    print("usage: separate.py FILENAME")
    sys.exit(1)

filename = sys.argv[1]

if not os.path.exists(DIRECTORY):
    os.makedirs(DIRECTORY)

with open(filename, 'r') as f:
    contents = f.readlines()


projects = []
new_csmake = []
current_project = ''
block_counter = 0


for line in contents:
    if line.startswith("#pragma echo"):
        continue
    if line.startswith("#pragma project"):
        start = line.find('\"')
        end = line.find('\"', start+1)
        current_project = line[start+1:end]
        projects.append(current_project)
        new_csmake.append(line)
        continue
    if line.startswith("#pragma block_enter"):
        block_counter += 1
        new_csmake.append(line)
        continue
    if line.startswith("#pragma block_exit"):
        block_counter -= 1
        new_csmake.append(line)
        if block_counter == 0:
            with open(can_project(current_project), 'w') as f:
                f.writelines(new_csmake)
                new_csmake = []
        continue
    new_csmake.append(line)

print(len(projects))
print(projects)
