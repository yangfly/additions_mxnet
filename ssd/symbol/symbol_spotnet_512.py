import mxnet as mx
import numpy as np
from spotnet_lighter3 import get_spotnet
from layer.multibox_target_layer import MultiBoxTarget, MultiBoxTargetProp
from layer.multibox_detection_layer import MultiBoxDetection, MultiBoxDetectionProp
from layer.softmax_loss_layer import SoftmaxLoss, SoftmaxLossProp
from layer.anchor_target_layer import *

def get_symbol_train(num_classes, **kwargs):
    '''
    '''
    fix_bn = False
    patch_size = 512
    per_cls_reg = True
    if 'patch_size' in kwargs:
        patch_size = kwargs['patch_size']

    preds, anchors = get_spotnet(num_classes, patch_size, per_cls_reg, use_global_stats=fix_bn)
    preds_cls = mx.sym.slice_axis(preds, axis=2, begin=0, end=num_classes) # (n_batch, n_anc, n_cls)
    probs_cls = mx.sym.SoftmaxActivation(mx.sym.transpose(preds_cls, (0, 2, 1)), mode='channel')
    preds_reg = mx.sym.slice_axis(preds, axis=2, begin=num_classes, end=None)

    label = mx.sym.var(name='label')

    tmp_in = [preds_cls, preds_reg, anchors, label, probs_cls]
    tmp = mx.symbol.Custom(*tmp_in, op_type='multibox_target', name='multibox_target',
            n_class=num_classes, variances=(0.1, 0.1, 0.2, 0.2), per_cls_reg=per_cls_reg)
    sample_cls = tmp[0]
    sample_reg = tmp[1]
    target_cls = tmp[2]
    target_reg = tmp[3]
    mask_reg = tmp[4]

    # classification
    cls_prob = mx.symbol.SoftmaxOutput(data=sample_cls, label=target_cls, \
        ignore_label=-1, use_ignore=True, grad_scale=1.0,
        normalization='null', name="cls_prob", out_grad=True)
    cls_loss = mx.symbol.Custom(cls_prob, target_cls, op_type='softmax_loss',
            ignore_label=-1, use_ignore=True)
    # alpha_cls = mx.sym.var(name='cls_beta', shape=(1,), lr_mult=0.1, wd_mult=0.0)
    # cls_loss_w = cls_loss * mx.sym.exp(-alpha_cls) + 10.0 * alpha_cls
    cls_loss = mx.sym.MakeLoss(cls_loss, name='cls_loss')

    # regression
    loc_diff = (sample_reg - target_reg) * mask_reg
    # masked_loc_diff = mx.sym.broadcast_mul(loc_diff, mask_reg)
    loc_loss = mx.symbol.smooth_l1(name="loc_loss_", data=loc_diff, scalar=1.0)
    loc_loss = mx.sym.sum(loc_loss) * 0.2
    # alpha_loc = mx.sym.var(name='loc_beta', shape=(1,),
    #         lr_mult=0.1, wd_mult=0.0, init=mx.init.Constant(2.0))
    # loc_loss_w = loc_loss * mx.sym.exp(-alpha_loc) + 10.0 * alpha_loc
    loc_loss = mx.symbol.MakeLoss(loc_loss, grad_scale=1.0, \
        normalization='null', name="loc_loss")

    label_cls = mx.sym.BlockGrad(target_cls, name='label_cls')
    label_reg = mx.sym.BlockGrad(mask_reg, name='label_reg')

    # group output
    out = mx.symbol.Group([cls_loss, loc_loss, label_cls, label_reg, mx.sym.BlockGrad(cls_prob)])
    # out = mx.symbol.Group([cls_loss_w, loc_loss_w, label_cls, label_reg, mx.sym.BlockGrad(cls_loss)])
    return out

def get_symbol(num_classes, **kwargs):
    '''
    '''
    # im_scale = mx.sym.Variable(name='im_scale')

    fix_bn = True
    patch_size = 512
    th_pos = 0.25
    th_nms = 1.0 / 3.0
    if 'patch_size' in kwargs:
        patch_size = kwargs['patch_size']
    if 'th_pos' in kwargs:
        th_pos = kwargs['th_pos']
    if 'nms' in kwargs:
        th_nms = kwargs['nms']

    preds, anchors = get_spotnet(num_classes, patch_size, use_global_stats=fix_bn)
    preds_cls = mx.sym.slice_axis(preds, axis=2, begin=0, end=num_classes)
    preds_reg = mx.sym.slice_axis(preds, axis=2, begin=num_classes, end=None)

    probs_cls = mx.sym.reshape(preds_cls, shape=(-1, num_classes))
    probs_cls = mx.sym.SoftmaxActivation(probs_cls)
    probs_cls = mx.sym.slice_axis(probs_cls, axis=1, begin=1, end=None)

    tmp = mx.symbol.Custom(*[probs_cls, preds_reg, anchors], op_type='multibox_detection',
            name='multibox_detection', th_pos=th_pos, n_class=num_classes-1, th_nms=th_nms, max_detection=128)
    return tmp

if __name__ == '__main__':
    import os
    os.environ['MXNET_ENGINE_TYPE'] = 'NaiveEngine'
    net = get_symbol_train(2, n_group=7, patch_size=768)

    mod = mx.mod.Module(net, data_names=['data'], label_names=['label'])
    mod.bind(data_shapes=[('data', (2, 3, 768, 768))], label_shapes=[('label', (2, 5))])
    mod.init_params()
    args, auxs = mod.get_params()
    for k, v in sorted(args.items()):
        print k + ': ' + str(v.shape)
    for k, v in sorted(auxs.items()):
        print k + ': ' + str(v.shape)