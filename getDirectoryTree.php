<?php
function parse_ls_tree_line($gitTreeLine) {
    list ($metadata, $filename) = explode("\t",$gitTreeLine);
    list ($mode, $obj_type, $obj_hash, $size) = preg_split('/\s+/', $metadata);
    return array ($filename, $mode, $obj_type, $obj_hash, $size);
}

function read_ls_tree_line($tree, $dataset, $dataset_directory, $gitTreeLine, $path="") {
    list ($filename, $mode, $obj_type, $obj_hash, $size) = parse_ls_tree_line(
        $gitTreeLine);
    # Skip git / datalad files
    if (substr($filename,0,4) === '.git')
        return $tree;
    if (substr($filename,0,8,) === '.datalad')
        return $tree;
    if (strcmp($filename,'.gitattributes') === 0)
        return $tree;

    if (strcmp($obj_type, 'blob') === 0) {
        array_push($tree, array(
            "text" => $filename,
            "href" => "https://raw.githubusercontent.com/OpenNeuroDatasets/$dataset/master/$path$filename"));
    }
    if (strcmp($obj_type, 'tree') === 0) {
        array_push($tree, array(
            "text" => $filename,
            "state" => array("expanded" => false),
            "nodes" => get_repo_files($dataset, $dataset_directory, $obj_hash, "$path$filename/")));
    }
    return $tree;
}
function get_repo_files($dataset, $dataset_directory, $branch='HEAD', $path='')
{
    $tree = array();
    $gitProcess = proc_open("git ls-tree -l $branch", array(1 => array("pipe","w")), $pipes, $dataset_directory, null);
    if (is_resource($gitProcess)) {
        while (($line = fgets($pipes[1])) !== false) {
            $gitTreeLine = rtrim($line);
            $tree = read_ls_tree_line($tree, $dataset, $dataset_directory, $gitTreeLine, $path);
        }
        proc_close($gitProcess);
    }
    return $tree;
}

$nemar_path = "/Users/dtyoung/Documents/NEMAR/openneuro_eeg";
$file = file('datasets.txt');
foreach ($file as $line) {
    if (!stripos($line, "processed")) {
        echo $line;
        $datasetId = trim($line);
        $dataset_directory = "$nemar_path/$datasetId";
        $out = fopen("data/$datasetId" . "TreeWithLinks.txt", "w");
        fwrite($out,json_encode((get_repo_files($datasetId, $dataset_directory))));
        fclose($out);
    }
}
?>
