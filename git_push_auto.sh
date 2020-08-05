#!/bin/bash


git add . 
git commit . -m"auto commit"
git push dropbox  --all -u > push_dropbox.log
git push github  --all -u > push_github.log
