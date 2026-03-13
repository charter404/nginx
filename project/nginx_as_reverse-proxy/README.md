###Project: Multi-Service Website Using NGINX Reverse Proxy

* Goal :
www.example.com
      |
      v
     NGINX
  /     |      \
Home   API   Portfolio
8001   8002    8003

* Each service runs separately, and NGINX routes traffic based on URL path.

* Example
www.example.com/          → Home service
www.example.com/api       → API service
www.example.com/portfolio → Portfolio service


## Step 1 : Create Project Structure
* Create folders for three services.

mkdir ~/reverse-proxy-project
cd ~/reverse-proxy-project

mkdir home-service
mkdir api-service
mkdir portfolio-service

* Final structure:
reverse-proxy-project
│
├── home-service
├── api-service
└── portfolio-service


## Step 2 : Create Virtual Environment for Each Service

* Example for home-service
    cd home-service
    python3 -m venv venvhome
    source venvhome/bin/activate
    pip install flask

* Create apphome.py
# home-service/app.py
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to Home Service"

if __name__ == "__main__":
    app.run(port=8001)

* Run
python apphome.py

* Open
http://localhost:8001


## Step 3: Create API Service

    cd ../api-service
    python3 -m venv venvapi
    source venvapi/bin/activate
    pip install flask

* Create API app:
from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/")
def api():
    return jsonify({"message": "API Service Working"})

if __name__ == "__main__":
    app.run(port=8002)

* Run:
    python appapi.py

* Test:
    http://localhost:8002



## Step 4: Create Portfolio Service

cd ../portfolio-service
python3 -m venv venvport
source venvport/bin/activate
pip install flask


* Create app:
from flask import Flask
app = Flask(__name__)

@app.route("/")
def portfolio():
    return "Portfolio Service Page"

if __name__ == "__main__":
    app.run(port=8003)


* Run:
    python appport.py
* Test:
    http://localhost:8003



## Step 5: Install NGINX
    sudo apt install nginx

* Start service:
    sudo systemctl start nginx



## Step 6: Configure Reverse Proxy in NGINX

* Create configuration file.
    sudo nano /etc/nginx/sites-available/reverse-proxy-project

* Add
server {

    listen 80;
    server_name www.example.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8002/;
    }

    location /portfolio/ {
        proxy_pass http://127.0.0.1:8003/;
    }

}


## Step 7: Enable Site

sudo ln -s /etc/nginx/sites-available/reverse-proxy-project /etc/nginx/sites-enabled/


## Step 8: Test Configuration

    sudo nginx -t
* Reload nginx:
    sudo systemctl reload nginx

## Step 9: Map Domain to Localhost

* Edit hosts file:
    sudo nano /etc/hosts
* Add:
    127.0.0.1   www.example.com

## Step 10: Test Reverse Proxy

* Open browser
* Home page:
    http://www.example.com
* API:
    http://www.example.com/api
* Portfolio:
    http://www.example.com/portfolio

* Each request goes through:
Browser
   |
   v
 NGINX Reverse Proxy
   |
   |---- Home Service (8001)
   |---- API Service (8002)
   |---- Portfolio Service (8003)




########### Important concept ####################


High level project :
    "Build a mini production stack with NGINX + Flask + Redis + PostgreSQL + Load Balancer"



* Difference between :
    proxy_pass http://127.0.0.1:8002/; 
               vs
    proxy_pass http://127.0.0.1:8002;


1️⃣   Without Trailing Slash
Nginx keeps the full original URL.
Example
* Nginx config:
location /api/ {
    proxy_pass http://127.0.0.1:8002;
}

* Client request:
http://example.com/api/users
* Forwarded to backend:
http://127.0.0.1:8002/api/users
✅ /api stays



2️⃣   With Trailing Slash

proxy_pass http://127.0.0.1:8002/;
* What happens
    Nginx removes the matched location part.
Example
* Config:
location /api/ {
    proxy_pass http://127.0.0.1:8002/;
}

* Client request:
http://example.com/api/users

* Forwarded to backend:
http://127.0.0.1:8002/users

❌ /api removed


🔑 Easy Rule To Remember

| proxy_pass                   | Result                |
| ---------------------------- | --------------------- |
| `proxy_pass http://server;`  | keeps path            |
| `proxy_pass http://server/;` | removes location part |


🔍 Visual Example

* Request:
    /api/products
* Location:
    location /api/

# Case 1
proxy_pass http://127.0.0.1:8002;

* Backend receives:
    /api/products

# Case 2
proxy_pass http://127.0.0.1:8002/;

* Backend receives:
    /products



🚀 When Each Is Used
* Use no slash
* When backend expects the same path.
Example:
    /api/users
    /api/products
* Use slash
* When backend doesn't know /api.
Example backend routes:
    /users
    /products


✅ One-line summary

;   → keep path
/;  → remove location prefix



🚀 The 10-Second Nginx Path Trick

Just compare the trailing slash between:
* location
* proxy_pass

Rule:
If proxy_pass has a trailing / → replace the location part
If proxy_pass has NO trailing / → keep the full path



################### Other way to understand #####################

## Case 1 — No Slash in proxy_pass
location /api/ {
    proxy_pass http://127.0.0.1:8002;
}

* Request:
    /api/users
* Backend receives:
    /api/users

✅ Path stays the same

Think:

Nginx = forward everything as-is



## Case 2 — Slash in proxy_pass
location /api/ {
    proxy_pass http://127.0.0.1:8002/;
}

* Request:
/api/users
* Backend receives:
/users

✅ Location prefix removed

Think:

/api/ → replaced with /


