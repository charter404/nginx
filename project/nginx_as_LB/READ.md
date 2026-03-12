NGINX will load balance requests between the two Python apps running in separate virtual environments.
Architecture:
www.example.com
       |
       v
     NGINX
    /     \
Template1   Template2
Python venv1   Python venv2
Port 8001      Port 8002

NGINX will load balance requests between the two Python apps running in separate virtual environments.


performing activity step by step

Step 1 - Project Structure


Example directory structure on Linux


template1/
 ├── venv/
 ├── app.py
 └── templates/

template2/
 ├── venv/
 ├── app.py
 └── templates/

Each template runs inside its own virtual environment




Step 2 - Create Virtual Environment for Template1


* Go to project folder:
    cd ~/webapps/template1
* Create virtual environment:
    python3 -m venv template1env
* Activate it:
    source template1env/bin/activate
* Install required packages (example Flask):
    pip install flask gunicorn


* Template1 Python App

from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Template1 Website"

if __name__ == "__main__":
    app.run(port=8001)

* Run:
    python app.py
* Template1 runs on:
    http://localhost:8001



Step 3 - Create Virtual Environment for Template2


* Go to project folder:
    cd ~/webapps/template2
* Create virtual environment:
    python3 -m venv template2env
* Activate it:
    source template2env/bin/activate
* Install required packages (example Flask):
    pip install flask gunicorn


* Template3 Python App

from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Template2 Website"

if __name__ == "__main__":
    app.run(port=8001)

* Run:
    python app.py
* Template2 runs on:
    http://localhost:8001



Step 4- Test Both Applications


* Open browser:
    http://localhost:8001 and http://localhost:8002
    both should work independent



Step5 -  Install NGINX

* Using command 
    sudo apt update
    sudo apt install nginx




Step 6 -Create NGINX Load Balancer Configuration


* Edit NGINX site config:
    sudo nano /etc/nginx/sites-available/example

* Add this configuration.
upstream python_templates {

    server 127.0.0.1:8001;
    server 127.0.0.1:8002;

}

server {

    listen 80;

    server_name www.example.com;

    location / {

        proxy_pass http://python_templates;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    }

}



Step 7 - Enable the Website
* Create symbolic link:
sudo ln -s /etc/nginx/sites-available/example /etc/nginx/sites-enabled/




Step 8 - Test NGINX Config
* Using command
    sudo nginx -t
* Expected output
    syntax is ok
    test is successful



Step 9 - Restart NGINX
* Using Command
    sudo systemctl reload nginx


Step 10 - Update Local DNS
* Edit hosts file: 
    sudo nano /etc/hosts
* Add:
    127.0.0.1   www.example.com



Step 11 - Test in Browser
* Open
    http://www.example.com




#########################

Other NGINX Load Balancing configuration are

By Default its  round robin.

## It can also be changed to east connection

upstream python_templates {

    least_conn;

    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}



## It can also be changed to Weighted load balancing
If template1 is stronger:
    server 127.0.0.1:8001 weight=3;
    server 127.0.0.1:8002 weight=1;


