#!/bin/bash
openssl req -out avatar.csr -newkey rsa:2048 -nodes -utf8 -keyout avatar.key -config avatar_openssl.cnf
echo "Sending CSR to on-line CA ..."
serial=`curl -s -X POST -F 'csr=@avatar.csr' http://lti.adabyron.uma.es/upload_csr/`
echo "Downloading certificate as $serial.crt, key saved as $serial.key"
mv avatar.key $serial.key
curl -s http://lti.adabyron.uma.es/$serial.crt > $serial.crt
rm avatar.csr
