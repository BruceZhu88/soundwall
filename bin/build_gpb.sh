#!/bin/sh

proto_dir=proto-files
out_dir=gpb

if [ ! -d "$proto_dir" ]; then
    echo "Downloading proto files...."
    git clone https://github.com/bang-olufsen/ase-fep-proto.git $proto_dir || {
        echo "Failed to download proto files for Soundwall!"
        exit 1
    }
fi

if [ ! -d "$out_dir" ]; then
    mkdir -p $out_dir
fi

echo "Genenrate poto files...."
for proto in $(ls $proto_dir/definitions/*.proto); do
    protoc -I=$proto_dir/definitions/ --python_out=$out_dir $proto
done

touch $out_dir/__init__.py
