from __future__ import division
import tensorflow as tf
import numpy as np
import os
# import scipy.misc
import PIL.Image as pil
from SfMLearner import SfMLearner
import glob

flags = tf.app.flags
flags.DEFINE_integer("batch_size", 4, "The size of of a sample batch")
flags.DEFINE_integer("img_height", 256, "Image height")
flags.DEFINE_integer("img_width", 832, "Image width")
flags.DEFINE_string("dataset_dir", "/disks/disk1/guohao/dataset/zhly/kitti_raw/", "Dataset directory")
flags.DEFINE_string("output_dir", "/disks/disk2/guohao/qjh_use/test_result", "Output directory")
flags.DEFINE_string("ckpt_file", "/disks/disk2/guohao/qjh_use/checkpoint2/", "checkpoint file")
FLAGS = flags.FLAGS

def main(_):
    #with open('/disks/disk1/guohao/dataset/zhly/kitti_raw/val.txt', 'r') as f:
     #   test_files = f.readlines()
     #   test_files = [FLAGS.dataset_dir + t[:-1] for t in test_files]
    #test_files = os.listdir(FLAGS.dataset_dir + "2011_09_26_drive_0091_sync_03")
    test_files = glob.glob(r"/disks/disk1/guohao/dataset/zhly/kitti_raw/2011_09_26_drive_0091_sync_03/*.jpg")
    test_files.sort()
    #for i in range(len(test_files)):
    #    test_files[i] = FLAGS.dataset_dir + "2011_09_26_drive_0091_sync_03/" + test_files[i]
    if not os.path.exists(FLAGS.output_dir):
        os.makedirs(FLAGS.output_dir)
    basename = os.path.basename(FLAGS.ckpt_file)
    output_file = FLAGS.output_dir + '/' + "test_deepth"
    sfm = SfMLearner()
    sfm.setup_inference(img_height=FLAGS.img_height,
                        img_width=FLAGS.img_width,
                        batch_size=FLAGS.batch_size,
                        mode='depth')
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    with tf.Session(config=config) as sess:
        saver = tf.train.Saver([var for var in tf.model_variables()])
        last_file = tf.train.latest_checkpoint(FLAGS.ckpt_file)
        saver.restore(sess, last_file)
        pred_all = []
        for t in range(0, len(test_files), FLAGS.batch_size):
            if t % 100 == 0:
                print('processing %s: %d/%d' % (basename, t, len(test_files)))
            inputs = np.zeros(
                (FLAGS.batch_size, FLAGS.img_height, FLAGS.img_width, 3),
                dtype=np.uint8)
            for b in range(FLAGS.batch_size):
                idx = t + b
                if idx >= len(test_files):
                    break
                #fh = open(test_files[idx], 'r')
                raw_im = pil.open(test_files[idx] ,'r')
                scaled_im = raw_im.resize((FLAGS.img_width, FLAGS.img_height), pil.ANTIALIAS)
                inputs[b] = np.array(scaled_im)
                # im = scipy.misc.imread(test_files[idx])
                # inputs[b] = scipy.misc.imresize(im, (FLAGS.img_height, FLAGS.img_width))
            pred = sfm.inference(inputs, sess, mode='depth')
            for b in range(FLAGS.batch_size):
                idx = t + b
                if idx >= len(test_files):
                    break
                print("pred:")
                print(pred['depth'][b,:,:,0])
                pred_all.append(pred['depth'][b,:,:,0])
        np.save(output_file, pred_all)

if __name__ == '__main__':
    tf.app.run()