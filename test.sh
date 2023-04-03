#!/bin/bash

conda env create -f environment.yml
conda activate stego
python dload_aoi.py
./split.sh
cd src
python download_models.py
python precompute_knns.py
python train_segmentation.py
