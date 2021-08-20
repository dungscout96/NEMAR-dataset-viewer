import subprocess
from subprocess import PIPE, STDOUT

nemar_path = '/Users/dtyoung/Documents/NEMAR/openneuro_test'
with open('datasets_test.txt','r') as f:
    with open('err.txt', 'w') as err:
        for line in f.readlines():
            if not line.__contains__("processed"):
                datasetId = line.strip()
                try:
                    gitProcess = subprocess.run(
                        ['datalad', 'get', '--dataset', f'{nemar_path}/{datasetId}'], stdout=PIPE, stderr=STDOUT, encoding='utf-8')
                except subprocess.CalledProcessError as error:
                    err.write(f'Error processing {datasetId}')
                    err.write('\t')
                    err.write(error.stderr)
                    err.write('\n')
