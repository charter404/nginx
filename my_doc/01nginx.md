NGINX step-by-step in the simplest way, including:
    * Nginx file structure
    * Configuration syntax
    * Load balancer configuration
    * Reverse proxy using paths
    * Least connections
    * IP hash
    * Weighted load balancing (for servers with different capacity)

########


1. NGINX Architecture
Think NGINX as traffic controller
Client -> NGINX -> Backend Servers


Users (Browser)
      |
      v
   NGINX
  /   |   \
192.168.1.2
192.168.1.3
192.168.1.4


2. NGINX file structure
Typical Linux Nginx directory structure

/etc/nginx/
│
├── nginx.conf
├── mime.types
├── conf.d/
│     └── default.conf
├── sites-available/
│     └── mysite
├── sites-enabled/
│     └── mysite -> symlink
├── snippets/
└── logs/


nginx.conf -> Main Configuration
conf.d/*.conf -> Additional configs
sites-available -> Available virtual hosts
sites-enabled -> Active virtual hosts
logs -> access.log and error.log



3. Main Nginx Configuration
nginx.conf

user nginx;
worker_processes auto;

events {
    worker_connections 1024;
}

http {

    include       mime.types;
    default_type  application/octet-stream;

    sendfile        on;

    include /etc/nginx/conf.d/*.conf;

}

* user nginx  -> NGINX worker processes run as nginx user
* worker_processes auto -> Defines number of worker processes, for better performance
    Example
        CPU cores = 4
        worker_processes = 4
* events block -> Defines how many connections each worker can handle
    Example
        worker_processes 4
        worker_connections 1024
    maximum connections:
        4 x 1024 = 4096

* http block -> All webserver configurations go inside this block
    Example -> reverse proxy, load balancing, caching, headers






4. Basic reverse proxy Example
* Backend Server
    App Server → 192.168.1.10:8080
* Nginx Config
server {
    listen 80;

    location / {
        proxy_pass http://192.168.1.10:8080;
    }
}

* How request Flows
User → http://website.com -> Request reaches nginx -> Nginx forwards request → 192.168.1.10:8080






5. NGINX as Load Balancer

* Servers:
    192.168.1.2
    192.168.1.3
    192.168.1.4

* Step 1 - Define Upstream
upstream backend_servers {

    server 192.168.1.2;
    server 192.168.1.3;
    server 192.168.1.4;

}

* Step 2 - Use upstream
server {
    listen 80;

    location / {
        proxy_pass http://backend_servers;
    }
}

* Request Flow
User Request
      |
      v
    NGINX
   /  |   \
 .2  .3   .4

* Nginx distributes traffic, Default algorithm -> Round Robin
    Example
    Request1 → .2
    Request2 → .3
    Request3 → .4
    Request4 → .2





6. Reverse Proxy with paths
* Paths :
        /home
        /aboutus
        /contact
        /portfolio
  Each Path -> different backends
    
* Example 
server {
    listen 80;

    location /home {
        proxy_pass http://192.168.1.2;
    }

    location /aboutus {
        proxy_pass http://192.168.1.3;
    }

    location /contact {
        proxy_pass http://192.168.1.4;
    }

    location /portfolio {
        proxy_pass http://192.168.1.2;
    }
}

* Request Flow :
    website.com/home → 192.168.1.2
    website.com/aboutus → 192.168.1.3
    website.com/contact → 192.168.1.4
    website.com/portfolio → 192.168.1.2





7. Least connection Load Balancing
* Default : Round Robin
    But sometimes severs have different loads
    Use -> least_conn
* Example
upstream backend_servers {

    least_conn;

    server 192.168.1.2;
    server 192.168.1.3;
    server 192.168.1.4;

}

* How it works
    NGINX sends request to server with least active connections
* Example
| Server      | Active Connections |
| ----------- | ------------------ |
| 192.168.1.2 | 10                 |
| 192.168.1.3 | 2                  |
| 192.168.1.4 | 7                  |

Next Request -> 192.168.1.3
because it has least load




8. IP Hash (session Persistence)
* Problem
    User login → request goes to different server → session lost.
* Solution
    ip_hash;
*Example
    upstream backend_servers {

    ip_hash;

    server 192.168.1.2;
    server 192.168.1.3;
    server 192.168.1.4;

}

* How it works
    NGINX hashes client IP
    Example -> User IP: 10.1.1.5 -> Always goes to: 192.168.1.3 -> so session remains same



9. Load balancer based on server capacity
* Scenario :
| Server      | Capacity       |
| ----------- | -------------- |
| 192.168.1.2 | High CPU + RAM |
| 192.168.1.3 | Low            |
| 192.168.1.4 | Low            |

use weight parameter

* Example
upstream backend_servers {

    server 192.168.1.2 weight=5;
    server 192.168.1.3 weight=1;
    server 192.168.1.4 weight=1;

}

* Traffic Distribution
    Total weight:
    5 + 1 + 1 = 7
Traffic split(High capacity server receives maximum traffic.)
| Server      | Traffic |
| ----------- | ------- |
| 192.168.1.2 | ~70%    |
| 192.168.1.3 | ~15%    |
| 192.168.1.4 | ~15%    |




10. Full Example Configuration

http {

upstream backend_servers {

    least_conn;

    server 192.168.1.2 weight=5;
    server 192.168.1.3 weight=1;
    server 192.168.1.4 weight=1;

}

server {

    listen 80;

    location /home {
        proxy_pass http://backend_servers;
    }

    location /aboutus {
        proxy_pass http://backend_servers;
    }

    location /contact {
        proxy_pass http://backend_servers;
    }

    location /portfolio {
        proxy_pass http://backend_servers;
    }

}

}




11. Important Proxy Headers
* Production NGINX usually includes
location / {
    proxy_pass http://backend_servers;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}


* Purpose
| Header          | Purpose                |
| --------------- | ---------------------- |
| Host            | Pass original hostname |
| X-Real-IP       | Client IP              |
| X-Forwarded-For | Track request path     |




12. How Request Actually Flows
* Example request:
    User → www.example.com/home
* Flow
    1 User sends request
    2 NGINX receives request
    3 Location block matches /home
    4 Proxy_pass forwards request
    5 Backend server processes request
    6 Response returns to NGINX
    7 NGINX sends response to user


















