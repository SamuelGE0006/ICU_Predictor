const express = require('express');
const upload = require('express-fileupload');
const path = require('path');
const fs = require('fs');
const app = express();

app.use(upload());
app.use("/css", express.static(path.join(__dirname, "node_modules/bootstrap/dist/css")));
app.use("/js", express.static(path.join(__dirname, "node_modules/bootstrap/dist/js")));
app.use(express.static('public/css'));

app.engine('html', require('ejs').renderFile);
app.set('view engine', 'html');

PORT_NUMBER = 8082;
app.listen(PORT_NUMBER, () => {
    console.log('Server Live at Port: ' + PORT_NUMBER);
});

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, "public", "views", "index.html"));
})

app.post('/', (req, res) => {
    if (req.files) {
        var file = req.files.file
        var filename = file.name

        file.mv('./uploads/' + filename, function (err) {
            if (err) {
                res.send(err);
            } else {
                var spawn = require('child_process').spawn;
                var filePath = path.join('uploads', filename);
                console.log(filePath);
                var process = spawn('python3', ["predict.py", filePath]);

                let output = '';
                process.stdout.on('data', function(data) {
                    output += data.toString();
                });
                process.on('close', () => {
                    console.log(output);
                    fs.unlinkSync(filePath);
                    res.redirect('/results');
                });
            }
        });
    }
})

app.get('/results', (req, res) => {
    // !!!
    res.sendFile(path.join(__dirname, "public", "views", "results.html"));
})

app.get('/explanation', (req, res) => {
    res.sendFile(path.join(__dirname, "public", "views", "explanation.html"));
})