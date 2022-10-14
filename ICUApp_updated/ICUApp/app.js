const express = require('express');
const upload = require('express-fileupload');
const path = require('path');
const fs = require('fs');
const app = express();

(function() {
    var childProcess = require("child_process");
    var oldSpawn = childProcess.spawn;
    function mySpawn() {
        console.log('spawn called');
        console.log(arguments);
        var result = oldSpawn.apply(this, arguments);
        return result;
    }
    childProcess.spawn = mySpawn;
})();


app.use(upload())

PORT_NUMBER = 8081;
app.listen(PORT_NUMBER, () => {
    console.log('Server Live at Port: ' + PORT_NUMBER);
});

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, "views", "index.html"));
})

app.post('/', (req, res) => {
    if (req.files) {
        var file = req.files.file
        var filename = file.name

        file.mv('./uploads/' + filename, function (err) {
            if (err) {
                console.log(err);
                res.send(err);
            } else {
                var spawn = require('child_process').spawn;
                var filePath = path.join('uploads', filename);
                console.log(filePath);
                var process = spawn('python3', ["predict.py", filePath]);
                process.stdout.on('data', function(data) {
                    console.log(data.toString());
                });
                process.on('close', () => {
                    fs.unlinkSync(filePath);
                    res.redirect('/explanation');
                });
            }
        });
    }
})

app.get('/explanation', (req, res) => {
    res.sendFile(path.join(__dirname, "views", "explanation.html"));
})