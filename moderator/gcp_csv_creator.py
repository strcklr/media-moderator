import os

LOCAL_DATA_PATH = "../../nsfw_data_scraper/data/"
GCS_BASE_URL = "gs://content_moderator_db/data/"
CLASS_NAMES = ["hentai", "porn", "neutral", "drawings", "sexy"]

def map_gcs_to_label(path_suffix, label):
    print("Building map for %s" % LOCAL_DATA_PATH + path_suffix)
    gcs_path = GCS_BASE_URL + path_suffix
    map = {}
    for (root,dirs,files) in os.walk(LOCAL_DATA_PATH + path_suffix, topdown=True):
        for f in files:
            map[gcs_path + str(f)] = label
        # print(map)
        print ('Completed!')
        print ('--------------------------------')
    return map

train_csv = {}
test_csv = {}

for label in CLASS_NAMES:
    train_csv.update(map_gcs_to_label("train/%s/" % label, label))
    test_csv.update(map_gcs_to_label("test/%s/" % label, label))

import csv

with open('test.csv', 'w') as f:
    print("Writing out test.csv...")
    for key in test_csv.keys():
        f.write("%s,%s\n"%(key,test_csv[key]))
    print("Complete!")

with open('train.csv', 'w') as f:
    print("Writing out train.csv...")
    for key in train_csv.keys():
        f.write("%s,%s\n"%(key,train_csv[key]))
    print("Complete!")