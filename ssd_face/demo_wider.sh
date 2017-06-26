#!/bin/bash
if [[ "$#" -lt 1 ]]; then
  echo "Image name not given."
  exit
fi
if [[ "$#" -gt 1 ]] 
then
  TH_POS=$2
else
  TH_POS=0.55
fi

python demo.py \
  --network spotnet_lighter3 \
  --images $1 \
  --dir image \
  --ext .jpg \
  --prefix model/spotnet_lighter3_bnfixed_768 \
  --epoch 1000 \
  --max-data-shapes 2560 2560 \
  --thresh $TH_POS \
  --gpu 1
  # --cpu 
