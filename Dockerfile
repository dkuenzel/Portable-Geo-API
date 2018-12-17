FROM alpine:3.8

# Create a group and user to run the api
RUN addgroup -S apigroup && adduser -S apiuser -G apigroup

RUN apk add --no-cache \
	libc-dev \
	gcc \
	python3 \
	python3-dev \
	postgresql-dev \
	&& \
	python3 -m ensurepip && \
	rm -r /usr/lib/python*/ensurepip && \
	pip3 install --upgrade pip setuptools && \
	if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
	if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
	rm -r /root/.cache

ADD ./requirements.txt /root/
RUN pip3 install -r /root/requirements.txt

RUN mkdir /home/apiuser/app
ADD ./app /home/apiuser/app/
ADD ./api.sh /home/apiuser/

WORKDIR /home/apiuser/
RUN chmod 755 -R /home/apiuser/*

# Tell docker that all future commands should run as the appuser user
USER apiuser

ENTRYPOINT ["/home/apiuser/api.sh"]
