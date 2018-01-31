FROM python:alpine3.6

ENV DIRECTORY="/zfssa-scripts/servers"
ENV TIMES="10:00 22:00"

# configure timezone
RUN apk add -U tzdata
RUN cp /usr/share/zoneinfo/America/Caracas /etc/localtime
RUN echo "America/Caracas" >  /etc/timezone
RUN apk del tzdata

# copy the content fo the repo to the image
ADD . /zfssa-scripts

# define the work directory
WORKDIR /zfssa-scripts

# install all packages from the requirements.txt file
RUN pip install -r requirements.txt

# run the program and adjust the times and directory to the ones you want
ENTRYPOINT ["./entrypoint.sh"]
