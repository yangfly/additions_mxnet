import mxnet as mx
from symbol.net_block import *


def prepare_groups(data, use_global_stats):
    ''' prepare basic groups '''
    # 48 24 12 6 3 1
<<<<<<< HEAD
    nf_3x3 = [256, 352, 448, 512, 512, 512]
    n_unit = [2, 2, 2, 2, 1, 1]
=======
    nf_3x3 = [(64, 64), (80, 80), (96, 96), (64, 64), (96,), ()]
    nf_1x1 = [128, 160, 192, 128, 96, 192]
    n_unit = [3, 3, 3, 2, 1, 1]
>>>>>>> d23cd8af5811b6e12c7558bbabd4fb008ec14716

    groups = []
<<<<<<< HEAD
    g = data
    for i, (nf3, nu) in enumerate(zip(nf_3x3, n_unit)):
        g = pool(g, kernel=(3, 3)) if i == 5 else pool(g)

        g = relu_conv_bn(g, 'g{}/init/'.format(i),
                num_filter=nf3, kernel=(3, 3), pad=(1, 1),
                use_global_stats=use_global_stats)
        for j in range(nu):
            g0 = g
            g = relu_conv_bn(g, 'g{}/{}/1x1/'.format(i, j),
                    num_filter=nf3/2, kernel=(1, 1), pad=(0, 0),
                    use_global_stats=use_global_stats)
            g = relu_conv_bn(g, 'g{}/{}/3x3/'.format(i, j),
                    num_filter=nf3, kernel=(3, 3), pad=(1, 1),
                    use_global_stats=use_global_stats)
            g = g + g0

        groups.append(g)

    nf_all = 512
    nf_sqz = 256

    # upsample, proj, concat, mix
    nf_up = [512 - i for i in nf_3x3[2::-1]]
    n_unit = [1, 1, 1]
    g = groups[3]
    for i, (gd, nf, nu) in enumerate(zip(groups[2::-1], nf_up, n_unit)):
        k = 2 - i
        gu = mx.sym.UpSampling(g, scale=2, num_filter=nf_all, sample_type='bilinear')
        gu = relu_conv_bn(gu, 'u{}/proj/'.format(k),
                num_filter=nf, kernel=(1, 1), pad=(0, 0),
                use_global_stats=use_global_stats)
        g = mx.sym.concat(gu, gd)
        g = relu_conv_bn(g, 'u{}/mix/'.format(k),
                num_filter=nf_all, kernel=(1, 1), pad=(0, 0),
                use_global_stats=use_global_stats)
        for j in range(nu):
            g0 = g
            g = relu_conv_bn(g, 'u{}/{}/1x1/'.format(i, j),
                    num_filter=nf_sqz, kernel=(1, 1), pad=(0, 0),
                    use_global_stats=use_global_stats)
            g = relu_conv_bn(g, 'u{}/{}/3x3/'.format(i, j),
                    num_filter=nf_all, kernel=(3, 3), pad=(1, 1),
                    use_global_stats=use_global_stats)
            g = g + g0
        groups[k] = g
=======
    for i, (nf3, nf1) in enumerate(zip(nf_3x3, nf_1x1)):
        kernel = (2, 2) if i < 5 else (3, 3)
        group_i = pool(group_i, kernel=kernel)
        group_i = relu_conv_bn(group_i, 'gi{}/'.format(i),
                num_filter=sum(nf3)+nf1, kernel=(1, 1), pad=(0, 0),
                use_global_stats=use_global_stats)

        for j in range(n_unit[i]):
            prefix_name = 'g{}/u{}/'.format(i, j)
            g0 = group_i
            group_i = conv_group(group_i, prefix_name,
                    num_filter_3x3=nf3, num_filter_1x1=nf1, do_proj=True,
                    use_global_stats=use_global_stats)
            group_i = group_i + g0

        # group_i = proj_add(group_i, g0, 'g{}/res/'.format(i), sum(nf3)+nf1, use_global_stats)
        groups.append([group_i])

    groups[0].append( \
            upsample_feature(groups[1][0], name='up10/', scale=2,
                num_filter_proj=64, num_filter_upsample=64, use_global_stats=use_global_stats))
    groups[0].append( \
            upsample_feature(groups[2][0], name='up20/', scale=4,
                num_filter_proj=256, num_filter_upsample=64, use_global_stats=use_global_stats))
    groups[1].append( \
            upsample_feature(groups[2][0], name='up21/', scale=2,
                num_filter_proj=64, num_filter_upsample=64, use_global_stats=use_global_stats))
    #
    # for i, g in enumerate(groups[2:-1], 3):
    #     pad = (1, 1) if i < 5 else (0, 0)
    #     d = relu_conv_bn(g[0], 'dn{}/'.format(i),
    #             num_filter=32, kernel=(3, 3), pad=pad, stride=(2, 2),
    #             use_global_stats=use_global_stats)
    #     groups[i].append(d)
>>>>>>> d23cd8af5811b6e12c7558bbabd4fb008ec14716

    return groups


def get_symbol(num_classes=1000, **kwargs):
    '''
    '''
    use_global_stats = kwargs['use_global_stats']

    data = mx.symbol.Variable(name="data")
    label = mx.symbol.Variable(name="label")

    conv1 = convolution(data, name='1/conv',
        num_filter=24, kernel=(4, 4), pad=(1, 1), stride=(2, 2), no_bias=True)  # 32, 198
    concat1 = mx.sym.concat(conv1, -conv1, name='1/concat')
    bn1 = batchnorm(concat1, name='1/bn', use_global_stats=use_global_stats, fix_gamma=False)
<<<<<<< HEAD
    pool1 = bn1
=======
    pool1 = bn1 #pool(bn1)
>>>>>>> d23cd8af5811b6e12c7558bbabd4fb008ec14716

    bn2_1 = relu_conv_bn(pool1, '2_1/',
            num_filter=24, kernel=(3, 3), pad=(1, 1), use_crelu=True,
            use_global_stats=use_global_stats)
    bn2_2 = relu_conv_bn(pool1, '2_2/',
            num_filter=16, kernel=(3, 3), pad=(1, 1),
            use_global_stats=use_global_stats)
    bn2 = mx.sym.concat(bn2_1, bn2_2)
    pool2 = pool(bn2)

    bn3_1 = relu_conv_bn(pool2, '3_1/',
            num_filter=24, kernel=(3, 3), pad=(1, 1), use_crelu=True,
            use_global_stats=use_global_stats)
    bn3_2 = relu_conv_bn(pool2, '3_2/',
            num_filter=80, kernel=(3, 3), pad=(1, 1),
            use_global_stats=use_global_stats)
    bn3 = mx.sym.concat(bn3_1, bn3_2)

    groups = prepare_groups(bn3, use_global_stats)
    nf_groups = [384, 384, 384, 256, 192, 192]

<<<<<<< HEAD
    hyper_groups = []
    nf_hyper = [256 for _ in groups]
=======
    for i, (nf, g) in enumerate(zip(nf_groups, groups)):
        g = mx.sym.concat(*g) if len(g) > 1 else g[0]
        g = relu_conv_bn(g, 'gc{}/'.format(i),
                num_filter=nf, kernel=(1, 1), pad=(0, 0),
                use_global_stats=use_global_stats)
        groups[i] = g

    hyper_groups = []
    nf_hyper = [192, 192, 192, 192, 192, 192]
>>>>>>> d23cd8af5811b6e12c7558bbabd4fb008ec14716

    for i, g in enumerate(groups):
        p1 = relu_conv_bn(g, 'hypercls/{}/0/'.format(i),
                num_filter=nf_hyper[i], kernel=(1, 1), pad=(0, 0),
                use_global_stats=use_global_stats)
        p1 = relu_conv_bn(p1, 'hypercls/{}/1/'.format(i),
                num_filter=nf_hyper[i], kernel=(1, 1), pad=(0, 0),
                use_global_stats=use_global_stats)
        h1 = mx.sym.Activation(p1, name='hyper{}/1'.format(i), act_type='relu')

        p2 = relu_conv_bn(g, 'hyperreg/{}/0/'.format(i),
                num_filter=nf_hyper[i], kernel=(1, 1), pad=(0, 0),
                use_global_stats=use_global_stats)
        p2 = relu_conv_bn(p2, 'hyperreg/{}/1/'.format(i),
                num_filter=nf_hyper[i], kernel=(1, 1), pad=(0, 0),
                use_global_stats=use_global_stats)
        h2 = mx.sym.Activation(p2, name='hyper{}/2'.format(i), act_type='relu')
        hyper_groups.append((h1, h2))

    pooled = []
    for i, h in enumerate(hyper_groups):
        hc = mx.sym.concat(h[0], h[1])
        p = mx.sym.Pooling(hc, kernel=(2, 2), global_pool=True, pool_type='max')
        pooled.append(p)

    pooled_all = mx.sym.flatten(mx.sym.concat(*pooled), name='flatten')
    fc1 = mx.sym.FullyConnected(pooled_all, num_hidden=4096, name='fc1')
    softmax = mx.sym.SoftmaxOutput(data=fc1, label=label, name='softmax')
    return softmax
