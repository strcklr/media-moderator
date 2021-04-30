# mp4-content-moderator

NOTE: This repository DOES NOT contain any NSFW content, besides some language used as categorization for the model.

This project scrubs an mp4 to determine if the video contains anything NSFW, with the goal of it eventually having a frontend component that would allow a user to drag and drop a video to be scrubbed. 

The goal of this project will be to introduce myself to commonly used cloud technologies (AWS EC2, GCP, Docker, etc.) as well as familiarize myself with common machine learning paradigms.

The dataset used for this project is from [this repository](https://github.com/strcklr/nsfw_data_scraper) (NOTE: this obviously contains NSFW language). All of the data has been uploaded to Google Cloud Storage and should be streamed directly from there when training the model.

