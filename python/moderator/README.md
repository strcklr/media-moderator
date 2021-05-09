# Moderator - Machine Learning Model

This is the source code for generating the model used in this project. 

## Requirements

This project uses [Python3](https://www.python.org/downloads/). See which version of Python you have installed as default using:

```bash
python --version
```

To specifically check your Python 3 version, run the following command:

```bash
python3 --version
```


## Installation

Run the following command to install requirements:

```bash
pip install -r requirements.txt
```

## Usage

There are two main ways to use the contents of this repository.

### Train a Model

1. Download the dataset. The dataset used for this project is from [this repository](https://github.com/strcklr/nsfw_data_scraper) (NOTE: this obviously contains NSFW language). To avoid having 50GBs of pornography on my computer, all of the data has been uploaded to Google Cloud Storage and will be streamed directly from there when training the model.
2. Run the following command to train the model:
```bash
python train.py
```
3. Wait while the model trains. Depending on your computer, this can take sever hours. Graphics card performance is a big factor in training speed. My 2020 MacBook Pro takes around 6 hours to train a model. In the future, I will be using moving training to some beefy cloud platform like Google Compute Engine to have speedier builds.

### Computing a Prediction

1. Download the file you would like to predict. Currently, only JPEG and MP4 file types are supported.
2. Run the following command:
```bash
python predict.py <PATH_TO_FILE>
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
