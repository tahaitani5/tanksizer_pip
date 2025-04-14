#!/bin/bash
set -e

docker \
    run \
    -it \
    --rm \
    -v dyreqtexample14:/app \
    -w /app \
    aco-miniforge \
    /bin/bash -c "conda install -y conda-build && conda-build --override-channels -c conda-forge --output-folder local-channel recipe"

ls -lah local-channel/noarch/
echo "Done!"
