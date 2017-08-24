import mxnet as mx
from symbol.net_block import *


def prepare_groups(group_i, data_shape, n_curr_ch, use_global_stats):
    '''
    '''
    # assume data_shape = 384

    # prepare filters
    # 48, 24, 12, 6, 3
    nf_3x3 = [(48, 72, 96), (64, 96, 128), (80, 120, 160), (64, 96), (96,)]
    nf_1x1 = [0, 0, 0, 64, 96]

    nf_dn = [32, 32, 32, 64, 64]

    # prepare groups
    n_group = len(nf_1x1)
    groups = []
    dn_groups = [[] for _ in nf_1x1]
    for i, (nf3, nf1) in enumerate(zip(nf_3x3, nf_1x1)):
        d = relu_conv_bn(group_i, 'dn{}/'.format(i),
                num_filter=nf_dn[i], kernel=(3, 3), pad=(1, 1), stride=(2, 2),
                use_global_stats=use_global_stats)
        dn_groups[i].append(d)

        group_i = pool(group_i)
        prefix_name = 'g{}/'.format(i)
        group_i = multiple_conv(group_i, prefix_name,
                num_filter_3x3=nf3, num_filter_1x1=nf1,
                use_global_stats=use_global_stats)
        # group_i = proj_add(gp, group_i, nfa, use_global_stats)
        groups.append(group_i)

    return groups, dn_groups


def upsample_groups(groups, use_global_stats):
    '''
    '''
    up_groups = [[] for _ in groups]
    up_groups[0].append( \
            upsample_feature(groups[1], name='up10/', scale=2,
                num_filter_proj=32, num_filter_upsample=32, use_global_stats=use_global_stats))
    up_groups[0].append( \
            upsample_feature(groups[2], name='up20/', scale=4,
                num_filter_proj=64, num_filter_upsample=32, use_global_stats=use_global_stats))
    up_groups[1].append( \
            upsample_feature(groups[2], name='up21/', scale=2,
                num_filter_proj=32, num_filter_upsample=32, use_global_stats=use_global_stats))
    return up_groups


def get_symbol(num_classes=1000, **kwargs):
    '''
    '''
    use_global_stats = kwargs['use_global_stats']
    data_shape = kwargs['data_shape']

    data = mx.symbol.Variable(name="data")
    label = mx.symbol.Variable(name="label")

    conv1 = convolution(data, name='1/conv',
        num_filter=24, kernel=(4, 4), pad=(1, 1), stride=(2, 2), no_bias=True)  # 32, 198
    concat1 = mx.sym.concat(conv1, -conv1, name='1/concat')
    bn1 = batchnorm(concat1, name='1/bn', use_global_stats=use_global_stats, fix_gamma=False)
    pool1 = pool(bn1) # 96
    bn2 = relu_conv_bn(bn1, '2_1/',
            num_filter=16, kernel=(3, 3), pad=(1, 1), stride=(2, 2),
            use_global_stats=use_global_stats)
    bn2 = mx.sym.concat(pool1, bn2, name='2/concat')

    bn31 = relu_conv_bn(bn2, '3_1/',
            num_filter=24, kernel=(3, 3), pad=(1, 1), use_crelu=True,
            use_global_stats=use_global_stats)
    bn32 = relu_conv_bn(bn2, '3_2/',
            num_filter=24, kernel=(3, 3), pad=(1, 1),
            use_global_stats=use_global_stats)
    bn3 = mx.sym.concat(bn31, bn32, name='3/concat')

    n_curr_ch = 72
    groups, dn_groups = prepare_groups(bn3, data_shape, n_curr_ch, use_global_stats)
    up_groups = upsample_groups(groups, use_global_stats)

    hyper_groups = []
    nf_hyper = 192

    for i, (g, u, d) in enumerate(zip(groups, up_groups, dn_groups)):
        p = mx.sym.concat(*([g] + d + u))
        p = relu_conv_bn(p, 'hyperconcat{}/'.format(i),
                num_filter=nf_hyper, kernel=(1, 1), pad=(0, 0),
                use_global_stats=use_global_stats)
        h = mx.sym.Activation(p, name='hyper{}'.format(i), act_type='relu')
        hyper_groups.append(h)

    pooled = []
    for i, h in enumerate(hyper_groups):
        p = mx.sym.Pooling(h, kernel=(2,2), global_pool=True, pool_type='max')
        pooled.append(p)

    pooled_all = mx.sym.flatten(mx.sym.concat(*pooled), name='flatten')
    # softmax = mx.sym.SoftmaxOutput(data=pooled_all, label=label, name='softmax')
    fc1 = mx.sym.FullyConnected(pooled_all, num_hidden=4096, name='fc1')
    softmax = mx.sym.SoftmaxOutput(data=fc1, label=label, name='softmax')
    return softmax
