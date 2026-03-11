
## Key Nginx directry and files (using for Ubuntu)

/etc/nginx/                # Main configuration folder
   nginx.conf              # Main config file
   sites-available/        # Place individual site configs here
   sites-enabled/          # Symlinks to active site configs
   conf.d/                 # Optional extra config snippets

/var/www/                  # Default web root
   html/                   # Default website
   templates/              # Our custom folder for multiple templates
       template1/
       template2/

#######

1.a -- /etc/nginx/nginx.conf
* The main config file
* Control global settings like:
    user www-data;           # The system user Nginx runs as
    worker_processes auto;   # Number of processes
    error_log /var/log/nginx/error.log;
    pid /run/nginx.pid;
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
Important : your site configs in sites-enabled/ are included here automatically


1.b -- /etc/nginx/sites-available and /sites-enabled/
* sites-available -> Stores all site configs(your template, default sites, etc)
* sites-enabled -> symlinks to configs in sites-available that you want active
Example
    /etc/nginx/sites-available/loadbalance-templates
    /etc/nginx/sites-enabled/loadbalance-templates -> ../sites-available/loadbalance-templates


1.c -- /var/www/ --web root
* This is where your actual HTML/CSS/JS files live
* In this case
    /var/www/templates/template1/index.html
    /var/www/templates/template2/index.html
The root directive in the Nginx config points to these folders:
server {
    listen 8081;
    root /var/www/templates/template1;
    index index.html;
}
* So any request to that server serves files from /var/www/templates/template1/

#######
2. How request flow in Nginx
Lets map loadbalance setup

Step 1 - User Request
    Browser goes to 
        http://templates.local
        - Port 80 by default
        - Host header -> templates.local

Step 2 - Nginx receives request
Nginx listen on port 80:
server {
    listen 80;
    server_name templates.local;
    location / {
        proxy_pass http://template_pool;
    }
}

* server_name matches templates.local
* location / means "all paths" (/, /index.html. /css/style.css, etc)

Step 3 - Load Balancer (upstream)
upstream template_pool {
    server 127.0.0.1:9001;
    server 127.0.0.1:9002;
}

* nginx picks one backend server (default: round robin)
* Example: first request -> 127.0.0.1:9001, second -> 127.0.0.1:9002
* proxy_pass forwards the request exactly like a client would

Step 4 - backend service responds
* if backend is python HTTP server:
    python3 -m http.server 9001
* or if backend is another Nginx serving /var/www/templates/template1/
    Request → Nginx on 8081 → serves index.html
* Response travels back through the load balancer to the browser

Step 5- Browser Render page
* Browser receives HTML/CSS/JS file
* Request for static asserts (/css/style.css) also go through load balancer -> backend

#######
3. How Nginx handles files internally
    i. Matching server block
        * Compares <Host> header with <server_name>
        * If multiple blocks match, first one is used
    ii. Matching location block
        * Find the best match for the request URL
        * location/ = catch-all
    iii. Root vs Proxy
        * root /var/www/...  -> serves file directory from disk
        * proxy_pass http://..  -> forwards request to another server
    iv. Upstream
        * Maintains list of backend servers 
        * Chooses server based on method (round-robin, least connections, ip_hash)
        * Forward request and returns the response

#######
4. Directry summary for setup
/etc/nginx/
    nginx.conf           # main config
    sites-available/
        loadbalance-templates  # load balancer config
        template1             # backend server 1
        template2             # backend server 2
    sites-enabled/
        loadbalance-templates -> ../sites-available/loadbalance-templates
        template1 -> ../sites-available/template1
        template2 -> ../sites-available/template2

/var/www/templates/
    template1/index.html
    template2/index.html

## Flow for request

Browser → Nginx load balancer (port 80)
       → picks backend (9001 or 9002)
       → backend serves index.html / static files
       → response back to Nginx
       → Nginx returns to browser 

✅ Key points

sites-available → all possible site configs
sites-enabled → only active ones
root → serves files from disk
proxy_pass → forwards request to another server
upstream → defines backends for load balancing
listen → the port Nginx accepts requests on (80 for normal HTTP)


#######
Overall Architecture (Load Balancer Flow)

                User Browser
                     │
                     │  http://templates.local
                     ▼
            ┌───────────────────┐
            │      Nginx        │
            │  Load Balancer    │
            │   listen :80      │
            └─────────┬─────────┘
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
   Backend Server 1        Backend Server 2
    (Template1)              (Template2)
    localhost:9001           localhost:9002
          │                       │
          ▼                       ▼
 /var/www/templates/       /var/www/templates/
      template1/                template2/
       index.html               index.html

What happens

    1️⃣ Browser requests:
        http://templates.local
    2️⃣ Nginx receives the request on port 80.
    3️⃣ Nginx checks its upstream pool.
    4️⃣ Request is forwarded to either:
        127.0.0.1:9001
        or
        127.0.0.1:9002
    5️⃣ Backend server returns HTML.
    6️⃣ Nginx sends response back to browser.

Round-Robin Load Balancing Example
    Request 1 → Template1
    Request 2 → Template2
    Request 3 → Template1
    Request 4 → Template2

    Visual:
    Client Requests
    Req1 ──► Nginx ──► Template1
    Req2 ──► Nginx ──► Template2
    Req3 ──► Nginx ──► Template1
    Req4 ──► Nginx ──► Template2
    (Default algorithm in Nginx)

Nginx Configuration Flow
        /etc/nginx/nginx.conf
                  │
                  ▼
       include /etc/nginx/sites-enabled/*
                  │
                  ▼
         loadbalance-templates


Inside that file:
upstream template_pool {
    server 127.0.0.1:9001;
    server 127.0.0.1:9002;
}

server {
    listen 80;
    server_name templates.local;

    location / {
        proxy_pass http://template_pool;
    }
}


Flow inside Nginx:
Incoming Request
        │
        ▼
Match server_name
        │
        ▼
Match location /
        │
        ▼
proxy_pass
        │
        ▼
Select upstream server
        │
        ▼
Forward request

###################
File System Layout

/etc/nginx/
│
├── nginx.conf
│
├── sites-available/
│      ├── loadbalance-templates
│      ├── template1
│      └── template2
│
└── sites-enabled/
       ├── loadbalance-templates
       ├── template1
       └── template2


/var/www/
│
└── templates/
      ├── template1/
      │     ├── index.html
      │     ├── css/
      │     ├── js/
      │     └── images/
      │
      └── template2/
            ├── index.html
            ├── css/
            ├── js/
            └── images/

########################

Static File Request Example
If the browser requests:
http://templates.local/css/style.css

Flow:
Browser
   │
   ▼
Nginx Load Balancer
   │
   ▼
Selected Backend
   │
   ▼
/var/www/templates/templateX/css/style.css


###############

Real-World Production Architecture
In production environments using Nginx, it often looks like this:
                Internet
                    │
                    ▼
           Nginx Load Balancer
              (Port 80 / 443)
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
     App Server   App Server   App Server
       NodeJS       Python       PHP
      Port 3000    Port 4000    Port 5000


Important concept:
Nginx does two completely different jobs depending on config:
| Directive    | What it does                       |
| ------------ | ---------------------------------- |
| `root`       | Serves files directly              |
| `proxy_pass` | Forwards request to another server |



















