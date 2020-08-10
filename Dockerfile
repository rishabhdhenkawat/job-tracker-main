#Use python as base image
FROM ubuntu:16.04

RUN apt-get update && \
	apt-get remove -y \
	x264 libx264-dev && \
	apt-get install -y \
	build-essential \
	checkinstall \
	cmake \
	pkg-config \
	libjpeg8-dev \
	libjasper-dev \
	libpng12-dev \
	libtiff5-dev \
	libtiff-dev \
	libavcodec-dev \
	libavformat-dev \
	libswscale-dev \
	libdc1394-22-dev \
	libxine2-dev \
	libv4l-dev

# Install system packages (python 3.5)

RUN apt-get install -y \
	python3-dev \
	python3-pip

# chrome install
RUN apt-get install wget
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN apt-get install curl -y
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set display port to avoid crash
ENV DISPLAY=:99


RUN  pip3 install -U pip
RUN pip install beautifulsoup4==4.9.1
RUN pip install bs4==0.0.1
RUN pip install certifi==2020.6.20
RUN pip install chardet==3.0.4
RUN pip install click==7.1.2
RUN pip install DateTime==4.3
RUN pip install Flask==1.1.2
RUN pip install html5lib==1.1
RUN pip install idna==2.10
RUN pip install itsdangerous==1.1.0
RUN pip install Jinja2==2.11.2
RUN pip install MarkupSafe==1.1.1
RUN pip install numpy
RUN pip install pandas
RUN pip install pymongo==3.10.1
RUN pip install python-dateutil==2.8.1
RUN pip install pytz==2020.1
RUN pip install requests==2.24.0
RUN pip install selenium==3.141.0
RUN pip install six==1.15.0
RUN pip install soupsieve==2.0.1
RUN pip install tqdm==4.48.0
RUN pip install urllib3==1.25.10
RUN pip install webencodings==0.5.1
RUN pip install Werkzeug==1.0.1
RUN pip install zope.interface==5.1.0


#ADD  . /
ADD . /todo
WORKDIR /todo


# Minimize image size 
RUN (apt-get autoremove -y; \
     apt-get autoclean -y)


#Run python program
#CMD ["python3","app.py"]
ENV SSH_PASSWD "root:Docker!"
RUN apt-get update \
       && apt-get install -y --no-install-recommends dialog \
       && apt-get update \
   && apt-get install -y --no-install-recommends openssh-server \
    && echo "$SSH_PASSWD" | chpasswd 

COPY sshd_config /etc/ssh/
COPY init.sh /usr/local/bin/
    
RUN chmod u+x /usr/local/bin/init.sh


EXPOSE 5000

#ENV NAME OpentoAll
#service SSH start
#CMD ["python3", "app.py"]

#ENTRYPOINT ["init.sh"]




