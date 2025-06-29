#dockerイメージを指定。
FROM python:3.12.3-slim-bookworm
RUN apt-get -y update && apt-get -y upgrade
#コンテナ内での作業ディレクトリを指定。
WORKDIR /root/app


RUN mkdir app
# Copy local code to the container image.
COPY . ./
#requirements.txtをコンテナ内のroot配下にコピー。
COPY requirements.txt requirements.txt
# コンテナ起動時にモジュールをインストール。
RUN pip install -r requirements.txt
#コンテナ起動時に実行するコマンドを指定。
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]