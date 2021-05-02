var express = require("express");
var request = require("request");
var https = require("https");

var app = express();


app.use(function(req, res, next) {
    res.set("Access-Control-Allow-Origin", "*");
    res.set("Access-Control-Expose-Headers", 'Content-Length');
	next();
});

var VIDEO_URL = "https://www.youtube.com/get_video_info?html5=1&video_id=";


app.get("/get-video-info", function(req, res) {
    request(VIDEO_URL + req.query.video_id, function(err, response) {
        if (err) res.status(500).send(err);
        res.send(response.body);
    });
});

app.listen(process.env.PORT || 8082);