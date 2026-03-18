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
ls
source venv/bin/activate
python3 /home/ubuntu/app.py
ls
cd ../webserver-course
cd webserver-course
ls
ls -a
cd ..
ss -tulpn | grep 5000
python3 /home/ubuntu/app.py
ss -tulpn | grep 5000
curl http://127.0.0.1:5000
source /home/ubuntu/venv/bin/activate
python3 /home/ubuntu/app.py
ss -tulpn | grep 5000
sudo nano /var/www/html/index.html
ls
cd venv
ls
cd ..
cd vwr
cd var
cd ..
ls
cd ..
ls
cd var
ls
ls -a
cd www
ls
nano html
cd html
ls
nano index.nginx-debian.html
sudo nano index.nginx-debian.html
cd ..
sudo nano /etc/nginx/sites-available/default
sudo systemctl restart nginx
sudo systemctl status nginx
python3 /home/ubuntu/app.py
sudo nano /etc/nginx/sites-available/default
sudo systemctl restart nginx
python3 /home/ubuntu/app.py
ss -tulpn | grep nginx
cat /etc/nginx/sites-available/default
pip install gunicorn
gunicorn -w 3 -b 127.0.0.1:5000 app:app
cd ..
cd /home/ubuntu
gunicorn -w 3 -b 127.0.0.1:5000 app:app
ss -tulpn | grep 5000
curl http://127.0.0.1:5000
kill 88996
ss -tulpn | grep 5000
kill -9 88996
ss -tulpn | grep 5000
cd /home/ubuntu
gunicorn -w 3 -b 127.0.0.1:5000 app:app
q
ss -tulpn | grep 5000
nano app.py
gunicorn -w 3 -b 127.0.0.1:5000 app:app
git --version
git config --global user.name "Giovan"
git config --global user.email "tu_email


git config --global user.name "Giovan"
git config --global user.email "giovan.ruiz.000@gmail.com"
cd /home/ubuntu
git init
git add .
git commit -m "initial commit
"
nano gitignore
cd ~
git remote add origin git@github.com:Giovan321/tenmiemail.com.git
git branch -M main
git push -u origin main
ssh-keygen -t ed25519 -C "giovan.ruiz.000@gmail.com"
cat ~/.ssh/id_ed25519.pub
ssh -T git@github.com
git push -u origin main
nano .gitignore
git rm -r --cached venv
git add .gitignore
git commit -m "remove venv and add gitignore"
git push
pip freeze > requirements.txt
cat requirements.txt

nano .gitignore
rm gitignore

git commit .m "add requiremtns"
git commit -m "add requiremtns"
git push
python3 /home/ubuntu/app.py
source venv/bin/activate
python3 /home/ubuntu/app.py
sudo -u postgres psql
exit
source venv/bin/activate
python3 /home/ubuntu/app.py
cd ~/ubuntu
ls
cd /home/ubuntu
ls
cat app.py
python3 /home/ubuntu/app.py
cd ..
cd .
cd ..
ls
cd ~/home
cd /home
ls
cd ..
find "postgrsql"
}mysql -u root -p
postgrsql -u root -p
sudo -u postgres psql
python3 /home/ubuntu/app.py
CREATE USER tu_user WITH PASSWORD 'tu_password';
ALTER DATABASE tu_db OWNER TO tu_user;
GRANT ALL PRIVILEGES ON DATABASE tu_db TO tu_user;
\q
pg_dump -U postgres -d users > backup.sql
sudo pg_dump -U postgres -d users > backup.sql
cd ~
pg_dump -U postgres -d users > backup.sql
sudo -u postgres pg_dump -d users > backup.sql
sudo -u postgres psql
sudo -u postgres pg_dump -d registros > backup.sql
