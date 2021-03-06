import os
from datetime import datetime
from utils import DotDict, namedtuple_with_defaults, zip_namedtuple, config_as_dict
import numpy as np

RandCropper = namedtuple_with_defaults('RandCropper',
    'min_crop_scales, max_crop_scales, \
    min_crop_aspect_ratios, max_crop_aspect_ratios, \
    min_crop_overlaps, max_crop_overlaps, \
    min_crop_sample_coverages, max_crop_sample_coverages, \
    min_crop_object_coverages, max_crop_object_coverages, \
    max_crop_trials',
    [0.0, 1.0,
    0.5, 2.0,
    0.0, 1.0,
    0.0, 1.0,
    0.0, 1.0,
    25])

RandPadder = namedtuple_with_defaults('RandPadder',
    'rand_pad_prob, max_pad_scale, fill_value',
    [0.0, 1.0, 127])

ColorJitter = namedtuple_with_defaults('ColorJitter',
    'random_hue_prob, max_random_hue, \
    random_saturation_prob, max_random_saturation, \
    random_illumination_prob, max_random_illumination, \
    random_contrast_prob, max_random_contrast',
    [0.0, 18,
    0.0, 32,
    0.0, 32,
    0.0, 0.5])


cfg = DotDict()
cfg.ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# training configs
cfg.train = DotDict()
# random cropping samplers
cfg.train.rand_crop_samplers = [
    RandCropper(min_crop_scales=0.3, min_crop_overlaps=0.1),
    RandCropper(min_crop_scales=0.3, min_crop_overlaps=0.3),
    RandCropper(min_crop_scales=0.3, min_crop_overlaps=0.5),
    RandCropper(min_crop_scales=0.3, min_crop_overlaps=0.7),
    RandCropper(min_crop_scales=0.3, min_crop_overlaps=0.9),]
cfg.train.crop_emit_mode = 'center'
# cfg.train.emit_overlap_thresh = 0.4
# random padding
cfg.train.rand_pad = RandPadder(rand_pad_prob=0.5, max_pad_scale=4.0)
# random color jitter
cfg.train.color_jitter = ColorJitter(random_hue_prob=0.5, random_saturation_prob=0.5,
    random_illumination_prob=0.5, random_contrast_prob=0.5)
cfg.train.inter_method = 10  # random interpolation
cfg.train.rand_mirror_prob = 0.5
cfg.train.shuffle = True
np.random.seed()
cfg.train.seed = np.random.randint(np.iinfo(np.int32).min, np.iinfo(np.int32).max)
cfg.train.preprocess_threads = 32

### [eldercrow] my additions
# cfg.train.mimic_fc = 2
cfg.train.use_focal_loss = True # focal loss
cfg.train.focal_loss_alpha = 1.0 / 4.0
cfg.train.focal_loss_gamma = 2.0
cfg.train.smoothl1_weight = 1.0 if cfg.train.use_focal_loss else 1.0
<<<<<<< HEAD
cfg.train.use_smooth_ce = True
cfg.train.smooth_ce_th = 1e-02
=======
cfg.train.use_smooth_ce = False
cfg.train.smooth_ce_th = 1e-03
>>>>>>> d23cd8af5811b6e12c7558bbabd4fb008ec14716
cfg.train.smooth_ce_lambda = 1.0

cfg.train = config_as_dict(cfg.train)  # convert to normal dict

# validation
cfg.valid = DotDict()
cfg.valid.rand_crop_samplers = []
cfg.valid.rand_pad = RandPadder()
cfg.valid.color_jitter = ColorJitter()
cfg.valid.rand_mirror_prob = 0
cfg.valid.shuffle = False
cfg.valid.seed = 0
cfg.valid.preprocess_threads = 32

### [eldercrow] my additions
cfg.valid.th_pos = 0.15
cfg.valid.th_nms = 0.45

cfg.valid = config_as_dict(cfg.valid)  # convert to normal dict
