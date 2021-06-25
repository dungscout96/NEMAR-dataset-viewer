import hashlib
import json
import subprocess

dataset = 'ds003004'
dataset_directory = f'/Users/dtyoung/Documents/NEMAR/{dataset}'

def compute_file_hash(git_hash, path):
    """Computes a unique hash for a given git path, based on the git hash and path values."""
    return hashlib.sha1('{}:{}'.format(git_hash, path).encode()).hexdigest()

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
    # # Check if the file is annexed or a submodule
    # if (mode == '120000'):
    #     # Save annexed file symlinks for batch processing
    #     symlinkFilenames.append(filename)
    #     symlinkObjects.append(obj_hash)
    # elif (mode == '160000'):
    #     # Skip submodules
    #     return
    # else:
    #     # Immediately append regular files
    #     file_id = compute_file_hash(obj_hash, filename)
    #     files.append({'filename': filename, 'size': int(size),
    #                   'id': file_id, 'key': obj_hash, 'urls': [], 'annexed': False})

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
    # # After regular files, process all symlinks with one git cat-file --batch call
    # # This is about 100x faster than one call per file for annexed file heavy datasets
    # catFileInput = '\n'.join(symlinkObjects)
    # catFileProcess = subprocess.run(['git', 'cat-file', '--batch', '--buffer'],
    #                                 cwd=dataset.path, stdout=subprocess.PIPE, input=catFileInput, encoding='utf-8')
    # # Output looks like this:
    # # dc9dde956f6f28e425a412a4123526e330668e7e blob 140
    # # ../../.git/annex/objects/Q0/VP/MD5E-s1618574--43762c4310549dcc8c5c25567f42722d.nii.gz/MD5E-s1618574--43762c4310549dcc8c5c25567f42722d.nii.gz
    # for index, line in enumerate(catFileProcess.stdout.splitlines()):
    #     # Skip metadata (even) lines
    #     if index % 2 == 1:
    #         key = line.rstrip().split('/')[-1]
    #         # Get the size from key
    #         size = int(key.split('-', 2)[1].lstrip('s'))
    #         filename = symlinkFilenames[(index - 1) // 2]
    #         file_id = compute_file_hash(key, filename)
    #         files.append({'filename': filename, 'size': int(
    #             size), 'id': file_id, 'key': key, 'urls': [], 'annexed': True})
    # Now find URLs for each file if available
    # return get_repo_urls(dataset.path, files)


print(json.dumps(get_repo_files(dataset, dataset_directory)))
