#!/bin/bash

openssl ca -batch -config openssl.cnf -passin pass:123456 -out newcert.pem -infiles $1 &> /dev/null
serial=`openssl x509 -in newcert.pem -noout -serial | cut -c 8-`
mv newcert.pem public/$serial.crt
echo $serial