In production environments, companies structure NGINX configuration in a modular, scalable, and maintainable way. Instead of writing everything in one file, they separate configurations into multiple files and directories so that large systems (with dozens or hundreds of services) remain manageable.

Below is the real-world structure used in many production environments.


1. Production NGINX Directory Structure
* Typically structure used by companies
/etc/nginx/
│
├── nginx.conf
├── mime.types
├── fastcgi_params
│
├── conf.d/
│   ├── upstreams.conf
│   ├── loadbalancer.conf
│
├── sites-available/
│   ├── api.example.com.conf
│   ├── app.example.com.conf
│   ├── admin.example.com.conf
│
├── sites-enabled/
│   ├── api.example.com.conf -> symlink
│   ├── app.example.com.conf -> symlink
│
├── upstreams/
│   ├── api_upstream.conf
│   ├── web_upstream.conf
│
├── snippets/
│   ├── proxy_headers.conf
│   ├── ssl.conf
│   ├── security.conf
│
├── logs/
│   ├── access.log
│   ├── error.log


* Why production companies structure it like this

| Directory       | Purpose              |
| --------------- | -------------------- |
| nginx.conf      | Main configuration   |
| conf.d          | global configs       |
| sites-available | all virtual hosts    |
| sites-enabled   | active sites         |
| upstreams       | backend server pools |
| snippets        | reusable configs     |




2. Main Production nginx.conf
* Production nginx.conf is usually very minimal

user nginx;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 4096;
}

http {

    include       mime.types;
    default_type  application/octet-stream;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;

    keepalive_timeout 65;

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}


* Why production teams do this
    This keep
    - main cinfig clean
    - service configs separate
    - easier CI/CD deployments




3. Upsteream Configuration(Production)
* Companies usually store Load balancer upsteram pools separately
* Example
/etc/nginx/upstreams/api_upstream.conf
upstream api_backend {

    least_conn;

    server 192.168.1.2 weight=5;
    server 192.168.1.3 weight=2;
    server 192.168.1.4 weight=2;

    keepalive 32;

}

* Why this is done
    Benefits
    - reuse upstream pools across multiple sites
    - easier scaling
    - easier server addition



4. Virtual Host Configuration
* Example
    /etc/nginx/sites-available/api.example.com.conf
server {

    listen 80;
    server_name api.example.com;

    location / {

        proxy_pass http://api_backend;

        include snippets/proxy_headers.conf;

    }

}


5. Reusable Snippets (production Best practice)
* Instead of repeating config everywhere, companies use snippets
* Example
    /etc/nginx/snippets/proxy_headers.conf

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

* Then include it:
    include snippets/proxy_headers.conf;
* Benefits
    Without snippets

proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

This would be repeated 100+ times



6. SSL Configuration (Production)
*Companies store SSL config separately
    /etc/nginx/snippets/ssl.conf
* Example
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;

* Usage :
server {

listen 443 ssl;

include snippets/ssl.conf;

ssl_certificate /etc/ssl/cert.pem;
ssl_certificate_key /etc/ssl/key.pem;

}




7. Security Configuration
* Production comapnies include security settings
* Example
    /etc/nginx/snippets/security.conf

    add_header X-Frame-Options SAMEORIGIN;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";



8. Multiple Services behind One Nginx
* Example company setup:
NGINX
 │
 ├── api.example.com → API servers
 ├── app.example.com → frontend servers
 ├── admin.example.com → admin backend

Example structure
sites-available/
    api.example.com.conf
    app.example.com.conf
    admin.example.com.conf

* Each site has separate configuration


9. production load balancer Example
* Example
upstream web_servers {

    least_conn;

    server 192.168.1.2 weight=5;
    server 192.168.1.3 weight=2;
    server 192.168.1.4 weight=2;

}
* Then
server {

listen 80;

location / {

proxy_pass http://web_servers;

}

}



10. Health Checks (production)

* Production systems monitor backend health.
* Example
    server 192.168.1.2 max_fails=3 fail_timeout=30s;
* Meaning
    If server fails 3 times within 30 seconds, remove it temporarily.


11. logging Strategy in production
* Companies separate logs
* Example:
    access_log /var/log/nginx/api_access.log;
    error_log  /var/log/nginx/api_error.log;
* Differnt services -> Different logs





12. CI/CD integration
* In modern DevOps environments (like what you work with):
* Deployment flow:
Git Repo
   |
   v
CI Pipeline
   |
   v
Test nginx config
   |
   v
Deploy to server
   |
   v
Reload nginx

* Commands used:
    nginx -t
    systemctl reload nginx


13. Production Scale Example
* Real world architecture
                Internet
                    |
               Cloud Load Balancer
                    |
                NGINX Cluster
            /          |          \
       API Servers  Web Servers  Auth Servers


