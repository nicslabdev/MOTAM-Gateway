const pemtools = require('pemtools');
const asn1js = require('asn1js');
const pkijs = require('pkijs');
const fs = require('fs');
const pvutils = require('pvutils');

//colored console output labeled for debuging
var debug = require('debug')('certificates');

const CryptoEngine = pkijs.CryptoEngine;

const WebCrypto = require('node-webcrypto-ossl');
const webcrypto = new WebCrypto();

//const assert = require("assert");
pkijs.setEngine('newEngine', webcrypto, new CryptoEngine({ name: '', crypto: webcrypto, subtle: webcrypto.subtle }));


//import { stringToArrayBuffer, bufferToHexCodes } from "pvutils";
//import { getCrypto, getAlgorithmParameters, setEngine } from "../../src/common.js";

//<nodewebcryptoossl>
//*********************************************************************************

const Certificate = pkijs.Certificate;
const RSAPublicKey = pkijs.RSAPublicKey;
const CertificateChainValidationEngine = pkijs.CertificateChainValidationEngine;
const CertificateRevocationList = pkijs.CertificateRevocationList;
const Extensions = pkijs.Extensions;


const CertificationRequest = pkijs.CertificationRequest;

/*******   EJEMPLOS DE USO  ***************
 
console.log("SERVIDOR")
console.log(util.inspect(parseCertificate("servidor.crt"))); 
console.log("CA")
console.log(util.inspect(parseCertificate("CA.crt"))); 
console.log('CSR');
csr = parsePKCS10('servidor.pem');
console.log(util.inspect(csr));
console.log(csr.signatureAlgorithm);
console.log(csr.signatureAlgorithm.toUpperCase().indexOf('SHA1')> -1);
console.log(csr.basicConstr.hasOwnProperty('cA'));
console.log(csr.basicConstr.cA);
console.log(csr.hasOwnProperty('subjectAltName'));
console.log(csr.subjectAltName.length);
console.log(csr.subjectAltName[0].value);
console.log(csr.publicKeySize);
console.log(csr.subject.findIndex(o => o.type === 'CN'));
console.log(csr.subject[0].value);
console.log("CRL")
console.log(util.inspect(parseCRL("CA.pem")));
console.log("Verify")
loadCertificate("servidor.crt").verify(loadCertificate("CA.crt")).then(result =>
{
	console.log(result);
}, error =>
{
	console.log("ERROR");
});
**************************************/

function loadCRL(filename)
{
	const crl = fs.readFileSync(filename, {encoding: 'utf8'});
	const crlBuffer = new Uint8Array(pemtools(crl, 'X509 CRL').toBuffer()).buffer;
	const asn1 = asn1js.fromBER(crlBuffer);
	const crlSimpl = new CertificateRevocationList({schema: asn1.result});
	return crlSimpl;
}

function loadPKCS10(csr)
{
	//const csr = fs.readFileSync(filename, {encoding: 'utf8'});
	const csr_buffer = new Uint8Array(pemtools(csr, 'CERTIFICATE REQUEST').toBuffer()).buffer;
	const asn1 = asn1js.fromBER(csr_buffer);
	const pkcs10 = new CertificationRequest({ schema: asn1.result });
	return pkcs10;
}

function loadCertificate(filename)
{
	var cert = fs.readFileSync(filename, {encoding: 'utf8'});
	var certificateBuffer = new Uint8Array(pemtools(cert, 'CERTIFICATE').toBuffer()).buffer;	
	const asn1 = asn1js.fromBER(certificateBuffer);
	const certificate = new Certificate({ schema: asn1.result });
	return certificate;
}

function parseCRL(filename)
{
	let result = {};

	const crl = fs.readFileSync(filename, {encoding: 'utf8'});
	const crlBuffer = new Uint8Array(pemtools(crl, 'X509 CRL').toBuffer()).buffer;
	//const asn1 = asn1js.fromBER(csr_buffer);
	//const pkcs10 = new CertificationRequest({ schema: asn1.result });

	if(crlBuffer.byteLength === 0)
	{
		return result;
	}


	const asn1 = asn1js.fromBER(crlBuffer);
	const crlSimpl = new CertificateRevocationList({
		schema: asn1.result
	});
	
	//region Put information about CRL issuer
	const rdnmap = {
		'2.5.4.6': 'C',
		'2.5.4.10': 'O',
		'2.5.4.11': 'OU',
		'2.5.4.3': 'CN',
		'2.5.4.7': 'L',
		'2.5.4.8': 'S',
		'2.5.4.12': 'T',
		'2.5.4.42': 'GN',
		'2.5.4.43': 'I',
		'2.5.4.4': 'SN',
		'1.2.840.113549.1.9.1': 'E-mail'
	};
	
	result.issuer = [];

	for(const typeAndValue of crlSimpl.issuer.typesAndValues)
	{	
		let typeval = rdnmap[typeAndValue.type];
		if(typeof typeval === 'undefined')
			typeval = typeAndValue.type;	
		const subjval = typeAndValue.value.valueBlock.value;
		result.issuer.push({type: typeval, value:subjval});
	
	}

	result.thisUpdate =  crlSimpl.thisUpdate.value.toString();
	
	result.nextUpdate =  crlSimpl.nextUpdate.value.toString();

	//region Put information about signature algorithm
	const algomap = {
		'1.2.840.113549.2.1': 'MD2',
		'1.2.840.113549.1.1.2': 'MD2 with RSA',
		'1.2.840.113549.2.5': 'MD5',
		'1.2.840.113549.1.1.4': 'MD5 with RSA',
		'1.3.14.3.2.26': 'SHA1',
		'1.2.840.10040.4.3': 'SHA1 with DSA',
		'1.2.840.10045.4.1': 'SHA1 with ECDSA',
		'1.2.840.113549.1.1.5': 'SHA1 with RSA',
		'2.16.840.1.101.3.4.2.4': 'SHA224',
		'1.2.840.113549.1.1.14': 'SHA224 with RSA',
		'2.16.840.1.101.3.4.2.1': 'SHA256',
		'1.2.840.113549.1.1.11': 'SHA256 with RSA',
		'2.16.840.1.101.3.4.2.2': 'SHA384',
		'1.2.840.113549.1.1.12': 'SHA384 with RSA',
		'2.16.840.1.101.3.4.2.3': 'SHA512',
		'1.2.840.113549.1.1.13': 'SHA512 with RSA'
	};       // array mapping of common algorithm OIDs and corresponding types
	
	let signatureAlgorithm = algomap[crlSimpl.signature.algorithmId];
	if(typeof signatureAlgorithm === 'undefined')
		signatureAlgorithm = crlSimpl.signature.algorithmId;
	else
		signatureAlgorithm = `${signatureAlgorithm} (${crlSimpl.signature.algorithmId})`;
	
	result.signatureAlgorithm = signatureAlgorithm;
	
	//region Put information about revoked certificates
	if('revokedCertificates' in crlSimpl)
	{
		result.revokedCertificates = [];
		for(let i = 0; i < crlSimpl.revokedCertificates.length; i++)
		{
			result.revokedCertificates.push({serial: pvutils.bufferToHexCodes(crlSimpl.revokedCertificates[i].userCertificate.valueBlock.valueHex), date:crlSimpl.revokedCertificates[i].revocationDate.value.toString()});
		}
	}
	//endregion
	//region Put information about CRL extensions
	if('crlExtensions' in crlSimpl)
	{
		result.crlExtensions = [];
		for(let i = 0; i < crlSimpl.crlExtensions.extensions.length; i++)
		{
			result.crlExtensions.push(crlSimpl.crlExtensions.extensions[i].extnID);
		}
		
	}
	//endregion
	return result;
}

function parsePKCS10(csr)
{

	const pkcs10 = loadPKCS10(csr);

	let result = {};
	
	//region Parse and display information about "subject"
	const typemap = {
		'2.5.4.6': 'C',
		'2.5.4.11': 'OU',
		'2.5.4.10': 'O',
		'2.5.4.3': 'CN',
		'2.5.4.7': 'L',
		'2.5.4.8': 'S',
		'2.5.4.12': 'T',
		'2.5.4.42': 'GN',
		'2.5.4.43': 'I',
		'2.5.4.4': 'SN',
		'1.2.840.113549.1.9.1': 'E-mail'
	};
	
	result.subject = [];

	for(const typeAndValue of pkcs10.subject.typesAndValues)
	{	
		let typeval = typemap[typeAndValue.type];
		if(typeof typeval === 'undefined')
			typeval = typeAndValue.type;	
		const subjval = typeAndValue.value.valueBlock.value;
		result.subject.push({type: typeval, value:subjval});
	
	}
	
	//region Put information about public key size
	let publicKeySize = '< unknown >';
	
	if(pkcs10.subjectPublicKeyInfo.algorithm.algorithmId.indexOf('1.2.840.113549') !== (-1))
	{
		const asn1PublicKey = asn1js.fromBER(pkcs10.subjectPublicKeyInfo.subjectPublicKey.valueBlock.valueHex);
		const rsaPublicKeySimple = new RSAPublicKey({ schema: asn1PublicKey.result });
		const modulusView = new Uint8Array(rsaPublicKeySimple.modulus.valueBlock.valueHex);
		let modulusBitLength = 0;
		
		if(modulusView[0] === 0x00)
			modulusBitLength = (rsaPublicKeySimple.modulus.valueBlock.valueHex.byteLength - 1) * 8;
		else
			modulusBitLength = rsaPublicKeySimple.modulus.valueBlock.valueHex.byteLength * 8;
		
		publicKeySize = modulusBitLength.toString();
	}
	
	result.publicKeySize = publicKeySize;
	
	//region Put information about signature algorithm
	const algomap = {
		'1.2.840.113549.1.1.2': 'MD2 with RSA',
		'1.2.840.113549.1.1.4': 'MD5 with RSA',
		'1.2.840.10040.4.3': 'SHA1 with DSA',
		'1.2.840.10045.4.1': 'SHA1 with ECDSA',
		'1.2.840.10045.4.3.2': 'SHA256 with ECDSA',
		'1.2.840.10045.4.3.3': 'SHA384 with ECDSA',
		'1.2.840.10045.4.3.4': 'SHA512 with ECDSA',
		'1.2.840.113549.1.1.10': 'RSA-PSS',
		'1.2.840.113549.1.1.5': 'SHA1 with RSA',
		'1.2.840.113549.1.1.14': 'SHA224 with RSA',
		'1.2.840.113549.1.1.11': 'SHA256 with RSA',
		'1.2.840.113549.1.1.12': 'SHA384 with RSA',
		'1.2.840.113549.1.1.13': 'SHA512 with RSA'
	};

	let signatureAlgorithm = algomap[pkcs10.signatureAlgorithm.algorithmId];
	if(typeof signatureAlgorithm === 'undefined')
		signatureAlgorithm = pkcs10.signatureAlgorithm.algorithmId;
	else
		signatureAlgorithm = `${signatureAlgorithm} (${pkcs10.signatureAlgorithm.algorithmId})`;
	
	result.signatureAlgorithm = signatureAlgorithm;


	//region Put information about PKCS#10 attributes
	if('attributes' in pkcs10)
	{
		for(let i = 0; i < pkcs10.attributes.length; i++)
		{
			const typeval = pkcs10.attributes[i].type;
			if(typeval === '1.2.840.113549.1.9.14')
			{
				const extensions = new Extensions({ schema: pkcs10.attributes[i].values[0] });
				extensions.extensions.forEach(function(element) {
					if (element.extnID == '2.5.29.19') //CA
					{
						result.basicConstr = element.parsedValue;
					}
					if (element.extnID == '2.5.29.18') //IssuerAltName
					{
						result.issuerAltName = element.parsedValue.altNames;
					}
					if (element.extnID == '2.5.29.17') //SubjectAltName
					{
						result.subjectAltName = element.parsedValue.altNames;
					}
					if (element.extnID == '2.5.29.15') //KeyUsage
					{
						// digitalSignature        (0)
						// nonRepudiation          (1) -- recent editions of X.509 have renamed this bit to contentCommitment
						// keyEncipherment         (2)
						// dataEncipherment        (3)
						// keyAgreement            (4)
						// keyCertSign             (5)
						// cRLSign                 (6)
						// encipherOnly            (7)
						// decipherOnly            (8)
						const view = new Uint8Array(element.parsedValue.valueBlock.valueHex);
						//console.log("Key keyUsage -> " + bits(view[0]));
						result.keyUsage= [];
						if((view[0] & 0x02) === 0x02) result.keyUsage.push('cRLSign');
						if((view[0] & 0x04) === 0x04) result.keyUsage.push('keyCertSign');
						if((view[0] & 0x08) === 0x08) result.keyUsage.push('keyAgreement');
						if((view[0] & 0x10) === 0x10) result.keyUsage.push('dataEncipherment');
						if((view[0] & 0x20) === 0x20) result.keyUsage.push('keyEncipherment');
						if((view[0] & 0x40) === 0x40) result.keyUsage.push('nonRepudiation');
						if((view[0] & 0x80) === 0x80) result.keyUsage.push('digitalSignature');
					}
				});
			} else
			{
				result.attributes = [];
				let subjval = '';	
				for(let j = 0; j < pkcs10.attributes[i].values.length; j++)
				{
					// noinspection OverlyComplexBooleanExpressionJS
					if((pkcs10.attributes[i].values[j] instanceof asn1js.Utf8String) ||
						(pkcs10.attributes[i].values[j] instanceof asn1js.BmpString) ||
						(pkcs10.attributes[i].values[j] instanceof asn1js.UniversalString) ||
						(pkcs10.attributes[i].values[j] instanceof asn1js.NumericString) ||
						(pkcs10.attributes[i].values[j] instanceof asn1js.PrintableString) ||
						(pkcs10.attributes[i].values[j] instanceof asn1js.TeletexString) ||
						(pkcs10.attributes[i].values[j] instanceof asn1js.VideotexString) ||
						(pkcs10.attributes[i].values[j] instanceof asn1js.IA5String) ||
						(pkcs10.attributes[i].values[j] instanceof asn1js.GraphicString) ||
						(pkcs10.attributes[i].values[j] instanceof asn1js.VisibleString) ||
						(pkcs10.attributes[i].values[j] instanceof asn1js.GeneralString) ||
						(pkcs10.attributes[i].values[j] instanceof asn1js.CharacterString))
					{
						subjval = subjval + ((subjval.length === 0) ? '' : ';') + pkcs10.attributes[i].values[j].valueBlock.value;
					}
					else
						subjval = subjval + ((subjval.length === 0) ? '' : ';') + pkcs10.attributes[i].values[j].constructor.blockName();
				}
				result.attributes.push({type: typeval, value:subjval});
			}
		}
		
	}
	return result;	
}

function parseCertificate(filename)
{
	let result = {};

	var cert = fs.readFileSync(filename, {encoding: 'utf8'});
	var certificateBuffer = new Uint8Array(pemtools(cert, 'CERTIFICATE').toBuffer()).buffer;	

	if(certificateBuffer.byteLength === 0)
	{
		return result;
	}

	const asn1 = asn1js.fromBER(certificateBuffer);
	const certificate = new Certificate({ schema: asn1.result });
	
	//region Put information about X.509 certificate issuer
	const rdnmap = {
		'2.5.4.6': 'C',
		'2.5.4.10': 'O',
		'2.5.4.11': 'OU',
		'2.5.4.3': 'CN',
		'2.5.4.7': 'L',
		'2.5.4.8': 'S',
		'2.5.4.12': 'T',
		'2.5.4.42': 'GN',
		'2.5.4.43': 'I',
		'2.5.4.4': 'SN',
		'1.2.840.113549.1.9.1': 'E-mail'
	};
	
	result.issuer = [];

	for(const typeAndValue of certificate.issuer.typesAndValues)
	{	
		let typeval = rdnmap[typeAndValue.type];
		if(typeof typeval === 'undefined')
			typeval = typeAndValue.type;	
		const subjval = typeAndValue.value.valueBlock.value;
		result.issuer.push({type: typeval, value:subjval});
	
	}

	result.subject = [];
	
	for(const typeAndValue of certificate.subject.typesAndValues)
	{
		let typeval = rdnmap[typeAndValue.type];
		if(typeof typeval === 'undefined')
			typeval = typeAndValue.type;		
		const subjval = typeAndValue.value.valueBlock.value;
		result.subject.push({type: typeval, value:subjval});

	}
	
	result.serial = pvutils.bufferToHexCodes(certificate.serialNumber.valueBlock.valueHex);
	
	result.notBefore = certificate.notBefore.value.toString();

	result.notAfter = certificate.notAfter.value.toString();
	
	//region Put information about subject public key size
	let publicKeySize = '< unknown >';
	
	if(certificate.subjectPublicKeyInfo.algorithm.algorithmId.indexOf('1.2.840.113549') !== (-1))
	{
		const asn1PublicKey = asn1js.fromBER(certificate.subjectPublicKeyInfo.subjectPublicKey.valueBlock.valueHex);
		const rsaPublicKey = new RSAPublicKey({ schema: asn1PublicKey.result });
		
		const modulusView = new Uint8Array(rsaPublicKey.modulus.valueBlock.valueHex);
		let modulusBitLength = 0;
		
		if(modulusView[0] === 0x00)
			modulusBitLength = (rsaPublicKey.modulus.valueBlock.valueHex.byteLength - 1) * 8;
		else
			modulusBitLength = rsaPublicKey.modulus.valueBlock.valueHex.byteLength * 8;
		
		publicKeySize = modulusBitLength.toString();
	}
	
	result.publicKeySize = publicKeySize;

	//region Put information about signature algorithm
	const algomap = {
		'1.2.840.113549.1.1.2': 'MD2 with RSA',
		'1.2.840.113549.1.1.4': 'MD5 with RSA',
		'1.2.840.10040.4.3': 'SHA1 with DSA',
		'1.2.840.10045.4.1': 'SHA1 with ECDSA',
		'1.2.840.10045.4.3.2': 'SHA256 with ECDSA',
		'1.2.840.10045.4.3.3': 'SHA384 with ECDSA',
		'1.2.840.10045.4.3.4': 'SHA512 with ECDSA',
		'1.2.840.113549.1.1.10': 'RSA-PSS',
		'1.2.840.113549.1.1.5': 'SHA1 with RSA',
		'1.2.840.113549.1.1.14': 'SHA224 with RSA',
		'1.2.840.113549.1.1.11': 'SHA256 with RSA',
		'1.2.840.113549.1.1.12': 'SHA384 with RSA',
		'1.2.840.113549.1.1.13': 'SHA512 with RSA'
	};       // array mapping of common algorithm OIDs and corresponding types
	
	let signatureAlgorithm = algomap[certificate.signatureAlgorithm.algorithmId];
	if(typeof signatureAlgorithm === 'undefined')
		signatureAlgorithm = certificate.signatureAlgorithm.algorithmId;
	else
		signatureAlgorithm = `${signatureAlgorithm} (${certificate.signatureAlgorithm.algorithmId})`;
	
	result.signatureAlgorithm = signatureAlgorithm;
	
	if('extensions' in certificate)
	{
		for(let i = 0; i < certificate.extensions.length; i++)
		{
			if (certificate.extensions[i].extnID == '2.5.29.19') //CA
			{
				result.basicConstr = certificate.extensions[i].parsedValue;
			}
			if (certificate.extensions[i].extnID == '2.5.29.18') //IssuerAltName
			{
				result.issuerAltName = certificate.extensions[i].parsedValue.altNames;
			}
			if (certificate.extensions[i].extnID == '2.5.29.17') //SubjectAltName
			{
				result.subjectAltName = certificate.extensions[i].parsedValue.altNames;
			}
			if (certificate.extensions[i].extnID == '2.5.29.15') //KeyUsage
			{
				// digitalSignature        (0)
				// nonRepudiation          (1) -- recent editions of X.509 have renamed this bit to contentCommitment
				// keyEncipherment         (2)
				// dataEncipherment        (3)
				// keyAgreement            (4)
				// keyCertSign             (5)
				// cRLSign                 (6)
				// encipherOnly            (7)
				// decipherOnly            (8)
				const view = new Uint8Array(certificate.extensions[i].parsedValue.valueBlock.valueHex);
				//console.log("Key keyUsage -> " + bits(view[0]));
				result.keyUsage= [];
				if((view[0] & 0x02) === 0x02) result.keyUsage.push('cRLSign');
				if((view[0] & 0x04) === 0x04) result.keyUsage.push('keyCertSign');
				if((view[0] & 0x08) === 0x08) result.keyUsage.push('keyAgreement');
				if((view[0] & 0x10) === 0x10) result.keyUsage.push('dataEncipherment');
				if((view[0] & 0x20) === 0x20) result.keyUsage.push('keyEncipherment');
				if((view[0] & 0x40) === 0x40) result.keyUsage.push('nonRepudiation');
				if((view[0] & 0x80) === 0x80) result.keyUsage.push('digitalSignature');
			}
		}
		
	}

	return result;
}

function verifyCertificate()
{
	
	//region Initial variables
	let sequence = Promise.resolve();
	//endregion
	
	//region Major activities
	sequence = sequence.then(() =>
	{

		const certChainVerificationEngine = new CertificateChainValidationEngine({
			trustedCerts: [loadCertificate('CA.crt')],
			certs: [loadCertificate('servidor.crt')],
			crls: [loadCRL('CA.pem')]
		});
		//region Verify CERT
		return certChainVerificationEngine.verify();
		//endregion
	});

	sequence = sequence.then(result => result, () => Promise.resolve(false));

	
	sequence.then(result =>
	{
		return result;
	}, error =>
	{
		debug(error);
		return '';
	});


}

module.exports.parseCertificate = parseCertificate;
module.exports.parseCRL = parseCRL;
module.exports.parseCSR = parsePKCS10;
module.exports.verifyCertificate = verifyCertificate;