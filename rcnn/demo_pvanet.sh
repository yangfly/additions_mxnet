#!/bin/bash
python demo_pvanet.py \
    --prefix /home/hyunjoon/github/model_mxnet/pva100/pva100 \
    --epoch 0 \
    --gpu 0 \
    --image /home/hyunjoon/faster-rcnn/data/demo/004545.jpg \
    --vis
    # --prefix /home/hyunjoon/github/additions_mxnet/rcnn/model/pvanet_voc0712 \
