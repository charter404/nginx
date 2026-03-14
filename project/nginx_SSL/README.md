####Project: Create SSL Certificate Manually + Deploy in Nginx


* Architecture:
Browser
   │
 HTTPS (443)
   │
Nginx
   │
Backend App (localhost:8000)

## Step 1 — Install OpenSSL
sudo apt install openssl

## Step 2 — Create SSL Certificate and Key
* Create a folder for certificates
    sudo mkdir /etc/nginx/ssl

* Generate certificate + key

sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/nginx.key -out /etc/nginx/ssl/nginx.crt

* You will be asked some questions.
Example:
Country Name: US
State: NY
Organization: MyCompany
Common Name: example.com

* After this you will have:
/etc/nginx/ssl/nginx.key
/etc/nginx/ssl/nginx.crt


## Step 3 — Configure Nginx HTTPS

* Edit site config.
sudo nano /etc/nginx/sites-available/mysslproject

* Add this:
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/nginx.crt;
    ssl_certificate_key /etc/nginx/ssl/nginx.key;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}


## Step 4 — Redirect HTTP → HTTPS

* Add another server block.

server {
    listen 80;
    server_name example.com;

    return 301 https://$host$request_uri;
}


## Step 5 — Enable the Site

sudo ln -s /etc/nginx/sites-available/mysslproject /etc/nginx/sites-enabled/

* Test config:
    sudo nginx -t
* Reload nginx:
    sudo systemctl reload nginx


## Step 6 — Test HTTPS

* Open browser:
    https://example.com
* You will see a warning:
    ⚠ Not Secure

This happens because self-signed certificates are not trusted by browsers.
But HTTPS still works.


### Verify Using curl
curl -k https://example.com
-k tells curl to ignore certificate trust errors.



📂 Final File Structure

/etc/nginx
│
├── ssl
│   ├── nginx.crt
│   └── nginx.key
│
├── sites-available
│   └── mysslproject
│
└── sites-enabled
    └── mysslproject


🔥 Bonus (Real Production Method)

Large companies usually use 3rd method:
CA Signed Certificates
Example providers:
- DigiCert
- Cloudflare
- AWS ACM
- GoDaddy

These provide trusted certificates like Let's Encrypt but often with extra enterprise features.

Nginx + Self-Signed SSL + Mutual TLS (mTLS)

This is used in microservices and banking systems.





