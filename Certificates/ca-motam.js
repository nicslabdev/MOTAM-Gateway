const express = require('express');
const app = express();
const fileUpload = require('express-fileupload');
app.use(express.static('./public'));
const port = 8080;
const crypto = require('crypto');
util = require('util');
const fs = require('fs');

const bodyParser = require('body-parser');

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));

// default options 
app.use(fileUpload());

//var sys = require('sys')
var exec = require('child_process').exec;
var execSync = require('child_process').execSync;
var error = false;

function isCsr(data){
  return data.indexOf("-----BEGIN CERTIFICATE REQUEST-----")+1;
}

function readCounter(){
  return fs.readFileSync('contador.txt');
}

function setCounter(contador){
  return fs.writeFileSync('contador.txt', contador)
}

function writeCsr(data,contador){
  let name = './csr/'+crypto.createHash('md5').update(contador.toString()).digest("hex")+'.csr';
  fs.writeFileSync(name, data)
  console.log('CSR saved as '+name);
  return name;
}

app.post('/upload_csr/', async (req, res, next) => {
  if ((req.files.csr) && (isCsr(req.files.csr.data)))
  {
    var csr = req.files.csr;

    let contador = parseInt(readCounter());  

    let name = writeCsr(csr.data,contador);
    setCounter(contador+1);
    salida = execSync("./sign.sh "+name);
    var serial = salida.toString()
    serial = serial.substring(0,serial.length-1);
    res.writeHead(200, {'content-type': 'text/html'});
    res.write(serial);         
    res.end();
    console.log(serial);
  } 

});

var server = app.listen(port, function (){
  var host = server.address().address;
  var port = server.address().port;
  console.log('CA MOTAM escuchando en el puerto', port);
});