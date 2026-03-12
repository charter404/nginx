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
