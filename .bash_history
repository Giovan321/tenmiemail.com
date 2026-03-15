ls -a
cd .ssh
ls -a
cd authorized_keys
nano authorized_keys
nano noexist
ls -a
nano ~/.ssh/authorized_keys
mkdir webserver-course
cd  webserver-course
sudo apt update
sudo apt upgrade -y
sudo apt install nginx -y
systemctl status nginx
ls
ls -l
cd ..
ls -l
ls -a
sudo mkdir -p /var/www/mywebsite
sudo nano /var/www/mywebsite/index.html
sudo ln -s /etc/nginx/sites-available/mywebsite /etc/nginx/sites-enabled/
sudo systemctl restart nginx
sudo nginx -t
sudo nano /etc/nginx/sites-available/mywebsite
sudo nano /var/www/mywebsite/index.html
sudo ln -s /etc/nginx/sites-available/mywebsite /etc/nginx/sites-enabled/
sudo systemctl restart nginx
sudo apt install postgresql postgresql-contrib -y
sudo -u postgres psql
sudo nano /var/www/mywebsite/index.html
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl status nginx
sudo ss -tulpn | grep 80
sudo apt install postgresql postgresql-contrib -y
sudo -u postgres psql
ls
ls -a
cd webserver-course
ls
sudo apt install python3-pip -y
pip install flask psycopg2-binary
nano app.py
python3 app.py
sudo apt install python3-venv -y
python3 -m venv venv
venv/
source venv/bin/activate
pip install flask psycopg2-binary
python app.py
sudo nano /etc/nginx/sites-available/mywebsite
sudo nginx -t
sudo systemctl restart nginx
python app.py
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx
app
python app.py
nano app.py
python app.py
app.py
nano Index.html
nano index.html
ls -a
cd webserver-course
ls -a
nginx
sudo nginx
cat /var/log/nginx/error.log
sudo nano /etc/nginx/sites-available/mywebsite
sudo nginx -t
sudo systemctl restart nginx
ptyhon app.py
python app.py
cd ..
python app.py
/var/www/mywebsite
cd /var/www/mywebsite
ls
nano index.html
sudo nano index.html
cd ..
sudo -u postgres psql
nano app.py
ls
find / -name app.py 2>/dev/null
nano /home/ubuntu/app.py
pyhton app.py
python app.py
python /home/ubuntu/app.py
sudo -u postgres psql
nano /home/ubuntu/app.py
python /home/ubuntu/app.py
sudo -u postgres psql
python3 /home/ubuntu/app.py
source venv/bin/activate
python3 /home/ubuntu/app.py
curl http://127.0.0.1:5000
