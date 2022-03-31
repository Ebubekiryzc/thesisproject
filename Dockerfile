FROM python:3

# Bu kod, python çıktılarının önce bufferda tutulup daha sonra bir block halinde konsola yazdırılmasındansa hiç tutulmadan yollanmasını sağlar.
ENV PYHTONUNBUFFERED=1

# Alttaki satırlar için bu klasörde çalıştır. 
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install -r requirements.txt

