# Create certs and test

1. Create the private certificate authority (CA) private and public keys:
```bash
$ openssl genrsa -out RootCA.key 4096
$ openssl req -new -x509 -days 3650 -key RootCA.key -out RootCA.pem
```

2. Create user certs with v3 extensions:
```bash
$ vi v3.ext
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
```

```bash
$ openssl genrsa -out client1.key 2048
$ openssl req -new -key client1.key -out client1.csr
$ openssl x509 -req -in client1.csr -extfile v3.ext -CA RootCA.pem -CAkey RootCA.key -CAcreateserial -out client1.pem -days 365
```

3. Create Server cert (common name add hostname mytest.mtls.com):
```bash
$ openssl genrsa -out srv.key 2048
$ openssl req -new -key srv.key -out srv.csr
$ openssl x509 -req -in srv.csr -CA RootCA.pem -CAkey RootCA.key -set_serial 01 -out srv.pem -days 3650 -sha256
```
4. view certs
```bash
$ openssl x509 -noout -text -in client1.pem
```

5. test (Fail)

```bash
curl --cacert RootCA.pem https://mytest.mtls.com
```

6. test (Success)

```bash
curl --cacert RootCA.pem --key client1.key --cert client1.pem https://mytest.mtls.com
```
