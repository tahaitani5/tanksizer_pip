#!/bin/bash
set -e

# Input Variables
HOME=`pwd`
BUILDER_CONFIG=${1:-$HOME/builder_config.json}
# Output Variables
FILES=$HOME/files_to_chevron.txt
INSTALLATION_PATH=$(cat $BUILDER_CONFIG | jq -r ".INSTALLATION_PATH")


# Make the INSTALLATION_PATH directory if it doesn't exist
mkdir -p $INSTALLATION_PATH

# Copy over the example (NOTE: doesn't copy dotfiles, we'll copy them over ourselves)
cp -r $HOME/template/example/* $INSTALLATION_PATH

# Find all the files in the example and store them in a file
find $HOME/template/example/ -mindepth 1 -type f -printf '%P\n' > $FILES

# Run the following commands in the INSTALLATION_PATH directory
cd $INSTALLATION_PATH

# Loop over the files in files_to_chevron
while IFS="" read -r FILE_TO_CHEVRON || [ -n "$FILE_TO_CHEVRON" ]; do
    echo "File: ${FILE_TO_CHEVRON}"

    # Copy the actual file over since dotfiles were ignored earlier
    cp $HOME/template/example/$FILE_TO_CHEVRON $INSTALLATION_PATH/$FILE_TO_CHEVRON
    
    # Run chevron on the file using the builder_config.json file and store the converted result back to the file
    printf "%s\n" "$(chevron -d $BUILDER_CONFIG $FILE_TO_CHEVRON)" > $FILE_TO_CHEVRON
done < $FILES

# Move the src subdirectory to the model name
MODEL_NAME=$(cat $BUILDER_CONFIG | jq -r ".MODULE_NAME")
mv $INSTALLATION_PATH/src/modelnamegoeshere $INSTALLATION_PATH/src/$MODEL_NAME
mv $INSTALLATION_PATH/tests/modelnamegoeshere $INSTALLATION_PATH/tests/$MODEL_NAME

# Mark the README.md with the specifics on the version of this repository used to create the example
cd $HOME
OUR_SHA=`git rev-parse HEAD`
echo "" >> $INSTALLATION_PATH/README.md
echo "## Template Note" >> $INSTALLATION_PATH/README.md
echo "This repository was created from the pip-installation-template code for commit https://gitlab.fit.nasa.gov/aco/mbe-infrastructure/pip-installation-template/-/tree/${OUR_SHA}" >> $INSTALLATION_PATH/README.md

# Clean up when we're done
rm -rf $FILES

echo "Complete!"
