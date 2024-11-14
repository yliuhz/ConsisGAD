#!/bin/bash

cd ..


[ -d logs ] || mkdir logs

# for DATASET in weibo reddit tolokers amazon tfinance yelp questions elliptic
for DATASET in amazon
do
CUDA_VISIBLE_DEVICES="5" python -u infer.py --config config/$DATASET.yml --runs 1 --thres 0.1 --comm_algo 'Louvain' 2>&1 | tee logs/infer_$DATASET.log
done

cd -