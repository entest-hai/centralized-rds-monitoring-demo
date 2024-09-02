FROM public.ecr.aws/docker/library/python:3.9 
WORKDIR /app
COPY . /app 
RUN python -m pip install -r requirements.txt 
ENTRYPOINT ["python"]
CMD ["app.py"]