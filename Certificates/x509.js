const fs = require('fs');
const crypto = require('crypto');
const path = require('path');

exports.isCsr = function (data){
  return data.indexOf("-----BEGIN CERTIFICATE REQUEST-----")+1;
}

exports.isCrt = function (data){
  return data.indexOf("-----BEGIN CERTIFICATE-----")+1;
}

exports.isCrl = function (data){
  return data.indexOf("-----BEGIN X509 CRL-----")+1;
}

exports.writeCsr = function (data){
  let contador = this.readAndIncreaseCounter();
  let name = './csr/'+crypto.createHash('md5').update(contador.toString()).digest("hex")+'.csr';
  fs.writeFileSync(name, data)
  return name;
}

exports.writeCrt = function (data){
  let contador = this.readAndIncreaseCounter();
  let name = './crt/'+crypto.createHash('md5').update(contador.toString()).digest("hex")+'.crt';
  fs.writeFileSync(name, data)
  return name;
}

exports.writeCa = function (data){
  let contador = this.readAndIncreaseCounter();
  let name = './ca/'+crypto.createHash('md5').update(contador.toString()).digest("hex")+'.crt';
  fs.writeFileSync(name, data)
  return name;
}

exports.writeCrl = function (data){
  let contador = this.readAndIncreaseCounter();
  let name = './crl/'+crypto.createHash('md5').update(contador.toString()).digest("hex")+'.crl';
  fs.writeFileSync(name, data)
  return name;
}

exports.empty = function (directory){

  fs.readdir(directory, (err, files) => {
    if (err) throw err;

    for (const file of files) {
      fs.unlink(path.join(directory, file), err => {
        if (err) throw err;
      });
    }
  });

  return 0;
}

exports.reset = function (){
  fs.writeFileSync('contador.txt', "0");
  folders = ["ca","crt","csr","crl"];
  for (var i = 0, len = folders.length; i < len; i++) 
  {
    if (fs.existsSync(folders[i]))
    {
      this.empty(folders[i]);
    } else
    {
      fs.mkdirSync(folders[i]);
    }
  }
  return 0;
}

exports.readAndIncreaseCounter = function (){
  return parseInt(fs.writeFileSync('contador.txt', parseInt(fs.readFileSync('contador.txt'))+1))
}

exports.setCounter = function (contador){
  return fs.writeFileSync('contador.txt', contador)
}

exports.readCounter = function (){
  return parseInt(fs.readFileSync('contador.txt'));
}
