#######################################################
FROM centos:7
RUN yum install -y  vim  httpd httpd-tools sed mod_ssl wget
RUN yum groupinstall -y 'development tools'
RUN yum install gcc openssl-devel bzip2-devel wget zlib-devel httpd-devel -y
RUN yum install sqlite-devel libffi-devel -y
RUN cd /usr/src/ && wget https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tar.xz
RUN cd /usr/src && tar xvf Python-3.9.0.tar.xz
RUN cd /usr/src/Python-3* && ./configure --enable-shared --enable-optimizations && make altinstall
RUN cd /usr/src &&  wget https://files.pythonhosted.org/packages/74/98/812e68f5a1d51e9fe760c26fa2aef32147262a5985c4317329b6580e1ea9/mod_wsgi-4.7.1.tar.gz
RUN cd /usr/src && tar xvf mod_wsgi-4.7.1.tar.gz
RUN touch /etc/ld.so.conf
RUN echo "/usr/local/lib" >> /etc/ld.so.conf
RUN echo "/usr/src/Python-3.9.0" >> /etc/ld.so.conf
RUN ldconfig -v
RUN cd /usr/src/mod_wsgi-4.7.1 && ./configure --with-python=/usr/local/bin/python3.9 && make && make install
RUN yum install python-devel mysql-devel -y
RUN pip3.9 install mysqlclient  
RUN useradd mailreader
RUN mkdir -p /home/mailreader/public_html/mail_reader
COPY . /home/mailreader/public_html/mail_reader
RUN mkdir -p /home/mailreader/logs
RUN mkdir -p /home/mailreader/public_html/mailreader_env/lib/python3.9/site-packages
RUN pip3.9 install -r /home/mailreader/public_html/mail_reader/requirements.txt
#CMD /home/mailreader/public_html/mailreader_env/bin/activate && pip install -r requirements.txt
WORKDIR /home/mailreader/public_html/mail_reader
#ENV PATH $PATH:/home/mailreader/public_html/mailreader_env/bin.
#ENV PATH $PATH:/home/mailreader/public_html/mailreader_env/bin/activate.
#RUN . /home/mailreader/public_html/mailreader_env/bin/activate 
#RUN pip install -r requirements.txt


RUN sleep 10 && echo "pip in running"
#ENV VIRTUAL_ENV=/home/mailreader/public_html/mail_reader
#ENV PATH="$VIRTUAL_ENV/bin:$PATH"
###########################################################################
#ADD baryons.net-0002.tar.gz  /home/mailreader/public_html/
#RUN mkdir -p /etc/letsencrypt/live/baryons.net-0002
##########################################################################
RUN echo "LoadModule wsgi_module modules/mod_wsgi.so" >> /etc/httpd/conf/httpd.conf
RUN echo "<VirtualHost *:80>" >> /etc/httpd/conf.d/test.conf
RUN echo "ServerName  172.105.38.216" >> /etc/httpd/conf.d/test.conf
RUN echo "DocumentRoot  /home/mailreader/public_html/mail_reader" >> /etc/httpd/conf.d/test.conf
#RUN echo "        RewriteEngine on" >> /etc/httpd/conf.d/test.conf
#RUN echo "ReWriteCond %{SERVER_PORT} !^443$" >> /etc/httpd/conf.d/test.conf
#RUN echo "RewriteRule ^/(.*) https://%{HTTP_HOST}/$1 [NC,R,L]" >> /etc/httpd/conf.d/test.conf
RUN echo "</VirtualHost>" >> /etc/httpd/conf.d/test.conf
#RUN echo "<VirtualHost *:443>" >> /etc/httpd/conf.d/test.conf
#RUN echo "ServerName 172.105.38.216" >> /etc/httpd/conf.d/test.conf
#RUN echo "DocumentRoot  /home/mailreader/public_html/mail_reader" >> /etc/httpd/conf.d/test.conf
#RUN echo "SSLEngine On" >> /etc/httpd/conf.d/test.conf
#RUN echo "SSLCertificateFile /home/mailreader/public_html/mail_reader/baryons.net-0002/cert1.pem" >> /etc/httpd/conf.d/test.conf
#RUN echo "SSLCertificateKeyFile /home/mailreader/public_html/mail_reader/baryons.net-0002/privkey1.pem" >> /etc/httpd/conf.d/test.conf
#RUN echo "SSLCertificateChainFile /home/mailreader/public_html/mail_reader/baryons.net-0002/fullchain1.pem" >> /etc/httpd/conf.d/test.conf
#RUN echo "ErrorLog /home/mailreader/logs/error.log" >> /etc/httpd/conf.d/test.conf
#RUN echo "TransferLog /home/mailreader/logs/access.log" >> /etc/httpd/conf.d/test.conf
RUN echo "WSGIPassAuthorization On" >> /etc/httpd/conf.d/test.conf
RUN echo "<Directory /home/mailreader/public_html/mail_reader>" >> /etc/httpd/conf.d/test.conf
RUN echo "<Files mailreader.wsgi>" >> /etc/httpd/conf.d/test.conf
RUN echo "Require all granted" >> /etc/httpd/conf.d/test.conf
RUN echo "</Files>" >> /etc/httpd/conf.d/test.conf
RUN echo "</Directory>" >> /etc/httpd/conf.d/test.conf
RUN echo "WSGIDaemonProcess mailreader python-path=/home/mailreader/public_html/mail_reader:/usr/local/lib/python3.9/site-packages" >> /etc/httpd/conf.d/test.conf
RUN echo "WSGIProcessGroup mailreader" >> /etc/httpd/conf.d/test.conf
RUN echo "WSGIScriptAlias / /home/mailreader/public_html/mail_reader/mailreader.wsgi process-group=mailreader" >> /etc/httpd/conf.d/test.conf
RUN echo "Alias /media /home/mailreader/public_html/mail_reader/media" >> /etc/httpd/conf.d/test.conf
RUN echo "<Directory /home/mailreader/public_html/mail_reader/media>" >> /etc/httpd/conf.d/test.conf
RUN echo "Require all granted" >> /etc/httpd/conf.d/test.conf
RUN echo "</Directory>" >> /etc/httpd/conf.d/test.conf
RUN echo "Alias /static /home/mailreader/public_html/mail_reader/static" >> /etc/httpd/conf.d/test.conf
RUN echo "<Directory /home/mailreader/public_html/mail_reader/static>" >> /etc/httpd/conf.d/test.conf
RUN echo "Require all granted" >> /etc/httpd/conf.d/test.conf
RUN echo "</Directory>"  >> /etc/httpd/conf.d/test.conf
#RUN echo "</VirtualHost>" >> /etc/httpd/conf.d/test.conf
RUN mkdir -p  /usr/share/httpd/nltk_data
RUN chmod -R 777 /usr/share/httpd/nltk_data
RUN chown -R apache:apache /home/mailreader
RUN chmod -R 775 /home/mailreader
EXPOSE 80
#WORKDIR /home/mailreader/public_html/mail_reader
###customizing the httpd configuration file for multiple projects ##default config....###
RUN sed -i 's/DirectoryIndex index.html/DirectoryIndex index.html index.php/g' /etc/httpd/conf/httpd.conf
###this is the virtual host configuration for the projects  ### Default config...###
RUN sed -i 's/AllowOverride none/AllowOverride all/g' /etc/httpd/conf/httpd.conf
RUN sed -i 's/AllOverride none/AllOverride all/g' /etc/httpd/conf/httpd.conf
RUN sed -i 's/UserDir disabled/#UserDir disabled/g' /etc/httpd/conf.d/userdir.conf
RUN sed -i 's/#UserDir public_html/UserDir public_html/g' /etc/httpd/conf.d/userdir.conf
RUN chown -R apache:apache /home
ENTRYPOINT ["/usr/sbin/httpd","-D","FOREGROUND"]


