#!/bin/bash
# from scratch
# python train.py \
#     --dataset wider_patch \
#     --image-set train \
#     --val-image-set '' \
#     --devkit-path /home/hyunjoon/dataset/wider \
#     --network spotnet_lighter_patch \
#     --batch-size 16 \
#     --from-scratch 1 \
#     --gpu 1 \
#     --prefix model/spotnet_lighter2_patch \
#     --data-shape 256 \
#     --end-epoch 1 \
#     --frequent 50 \
#     --lr 1e-03 \
#     --wd 1e-04
    # --monitor 1000 \

# full training
python train.py \
    --dataset wider \
    --image-set train \
    --val-image-set '' \
    --devkit-path /home/hyunjoon/dataset/wider \
    --network spotnet_lighter_bnfixed \
    --batch-size 4 \
    --gpu 1 \
    --prefix model/spotnet_lighter2_clonefixed2 \
    --data-shape 768 \
    --frequent 800 \
    --lr 1e-04 \
    --lr-factor 0.1 \
    --lr-steps 3,4 \
    --wd 1e-04 \
    --pretrained model/spotnet_lighter2_bnfixed_768 \
    --epoch 0
    # --resume 11 
    # --monitor 2000 \
    # --lr-steps 10,15,18,21 \
