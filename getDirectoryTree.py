import json
import subprocess
import os

def parse_ls_tree_line(gitTreeLine):
    """Read one line of `git ls-tree` output and produce filename + metadata fields"""
    metadata, filename = gitTreeLine.split('\t')
    mode, obj_type, obj_hash, size = metadata.split()
    return [filename, mode, obj_type, obj_hash, size]

def read_ls_tree_line(tree, dataset, dataset_directory, gitTreeLine, path=''):
    """Read one line of `git ls-tree` and append to the correct buckets of files, symlinks, and objects."""
    filename, mode, obj_type, obj_hash, size = parse_ls_tree_line(
        gitTreeLine)
    # Skip git / datalad files
    if filename.startswith('.git'):
        return
    if filename.startswith('.datalad'):
        return
    if filename == '.gitattributes':
        return

    if obj_type == "blob":
        tree.append({"text": filename, "href": f"https://raw.githubusercontent.com/OpenNeuroDatasets/{dataset}/master/{path}{filename}"})
    if obj_type == "tree":
        tree.append({"text": filename, "state": {"expanded": False}, "nodes": get_repo_files(dataset, dataset_directory, obj_hash, path=f"{path}{filename}/")})



def get_repo_files(dataset, dataset_directory, branch='HEAD', path=''):
    tree = []
    """Read all files in a repo at a given branch, tag, or commit hash."""
    gitProcess = subprocess.Popen(
        ['git', 'ls-tree', '-l', branch], cwd=dataset_directory, stdout=subprocess.PIPE, encoding='utf-8')
    for line in gitProcess.stdout:
        gitTreeLine = line.rstrip()
        read_ls_tree_line(tree, dataset, dataset_directory, gitTreeLine, path)
    return tree

nemar_path = '/Users/dtyoung/Documents/NEMAR/openneuro_datasets'
with open('openneuro_datasets_cont','r') as f:
    for line in f.readlines():
        if not line.__contains__("processed"):
            datasetId = line.strip()
            if not os.path.isfile(f'data/{datasetId}TreeWithLinks.txt'):
                print(f'processing {datasetId}...')
                dataset_directory = f'{nemar_path}/{datasetId}'
                try:
                    gitProcess = subprocess.run(
                        ['datalad', 'install', f'https://github.com/OpenNeuroDatasets/{datasetId}.git'], check=True, cwd=nemar_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    with open(f'data/{datasetId}TreeWithLinks.txt', 'w') as out:
                        out.write(json.dumps(get_repo_files(datasetId, dataset_directory)))
                except subprocess.CalledProcessError:
                    print(f'Error processing {datasetId}. Move on')
