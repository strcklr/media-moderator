import tensorflow._api.v2.compat.v1 as tf
import numpy as np
import cv2
import os
import psutil
import multiprocessing as mp
from tqdm import tqdm

LOCAL_DATA_PATH = "S://data/"
OUTPUT_DIR = "G://tfrecords/"
GCS_BASE_URL = "gs://content_moderator_db/data/"
CLASS_NAMES = ["hentai", "porn", "neutral", "drawings", "sexy"]
label_map = {
    "drawings": 0,
    "hentai": 1,
    "neutral": 2,
    "porn": 3,
    "sexy": 4
}


def _int64_feature(value):
    return tf.train.Feature(
        int64_list=tf.train.Int64List(value=value)
    )


def _floats_feature(value):
    return tf.train.Feature(
        float_list=tf.train.FloatList(value=value)
    )


def _bytes_feature(value):
    return tf.train.Feature(
        bytes_list=tf.train.BytesList(value=value)
    )


def load_image(path):
    img = cv2.imread(path)
    # cv2 load images as BGR, convert it to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32)
    return img


def get_feature(image, label):
    return {  # split to channels just for clearer representation, you may also encode it as image.reshape(-1)
        'r': _floats_feature(image[:, :, 0].reshape(-1)),
        'g': _floats_feature(image[:, :, 1].reshape(-1)),
        'b': _floats_feature(image[:, :, 2].reshape(-1)),
        'label': _int64_feature([label])
    }


def process_write(paths, labels, split, max_bytes, process_id):
    shard_count, i = 0, 0
    n_examples = len(paths)


    if not os.path.isdir('%s%s' % (OUTPUT_DIR, split)):
        os.mkdir('%s%s' % (OUTPUT_DIR, split))

    while i != n_examples:
        output_file_path = '{path}/{split}/{process_id}-shard{shard}.tfrecords'.format(path=OUTPUT_DIR,split=split, process_id=process_id, \
                                                                                     shard=shard_count)

        with tf.python_io.TFRecordWriter(output_file_path) as writer:
            while os.stat(output_file_path).st_size < max_bytes and i != n_examples:
                try:
                    print("Creating example for path: %s, label: %s" % (paths[i], labels[i]))
                    img = load_image(paths[i])
                    example_i = tf.train.Example(
                        features=tf.train.Features(
                            feature=get_feature(
                                img,
                                label_map[labels[i]])
                        ))
                    writer.write(example_i.SerializeToString())
                except Exception as e:
                    print("WARNING: Unable to read image %s" % paths[i])
                i += 1
        shard_count += 1
    return 1


def split2records(paths, labels, split, max_bytes=1e9):
    """
    Takes in a list of file paths to write to a TFRecord
    """

    print('Starting processing split {}.'.format(split))

    # number of shutdowns + restarts to maintain ~1sec/iteration of encoding
    # if factor = 1 it can go up to ~11sec/iteration (really slow)
    # larger value = faster single processes but more shutdown/startup time
    # smaller value = slower single process but less shutdown/startup time
    factor = 70
    n_processes = psutil.cpu_count() - 3
    print('Using {} processes...'.format(n_processes))

    path_split = np.array_split(paths, factor)
    label_split = np.array_split(labels, factor)

    process_id = 0
    pbar = tqdm(total=factor)

    for m_paths, m_labels in zip(path_split, label_split):
        paths_further_split = np.array_split(m_paths, n_processes)
        labels_further_split = np.array_split(m_labels, n_processes)

        pool = mp.Pool(n_processes)  # multiprocess writing because we don't have all day
        returns = []

        for split_paths, split_labels in zip(paths_further_split, labels_further_split):
            r = pool.apply_async(process_write, args=(split_paths, split_labels, split, max_bytes, process_id))
            returns.append(r)
            process_id += 1

        pool.close()
        for r in returns: r.get()
        pool.join()
        pbar.update(1)
    pbar.close()

    # for f in path_split:
    #     r = pool.apply_async(get_example, args=(writer, base_path + f, label))
    #
    #     # if i % 25 == 0:
    #     #     print("{index} Creating records - {index}/{total} ({percent}%)".format(index=i / 25,
    #     #                                                                            total=(len(files)),
    #     #                                                                            percent=(i / len(
    #     #                                                                                files)) * 100))
    #     # i += 1
    #     #
    #     #     print(
    #     #         "-------------------------------------------------------------------------------------------------------------------")


def gather_paths(split):
    """
    Gathers all files within the split directory
    :param split: the split, e.g. train, test, validation
    :return: a list of absolute paths to files
    """
    path_list = []
    label_list = []
    for label in CLASS_NAMES:
        path = LOCAL_DATA_PATH + split + "/" + label
        print("[{label}] Gathering files for path {path}...".format(label=label, path=path))
        total = len(os.listdir(path))
        for f in os.listdir(path):
            path_list.append(os.path.join(path, f))
            label_list.append(label)
        print("------ Gathered {num} files!\n".format(num=total))
    print(
        "-------------------------------------------------------------------------------------------------------------------")
    print("Total gathered files: {total}\n".format(total=len(path_list)))
    return path_list, label_list


if __name__ == '__main__':
    for split in ['train', 'test']:
        files, labels = gather_paths(split)
        split2records(files, labels, split)
