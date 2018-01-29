FROM python:alpine3.6

# configure timezone
RUN apk add -U tzdata
RUN cp /usr/share/zoneinfo/America/Caracas /etc/localtime
RUN echo "America/Caracas" >  /etc/timezone
RUN apk del tzdata

# copy the content fo the repo to the image
ADD . /zfssa-scripts
RUN mkdir /zfssa-scripts/servers
RUN mkdir /zfssa-scripts/data

# define the work directory
WORKDIR /zfssa-scripts

# install all packages from the requirements.txt file
RUN pip install -r requirements.txt

# run the program and adjust the times and directory to the ones you want
ENTRYPOINT ["python", "-u", "explorer_scheduler.py", "-d", "/zfssa-scripts/servers", "-t", "10:00", "-t", "22:00"]
