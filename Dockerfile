FROM masood09/django-development:0.1.0
ENV HOME /root
ENV APP_HOME /application/
ADD requirements.txt $APP_HOME
RUN pip install -r requirements.txt
ADD . $APP_HOME
