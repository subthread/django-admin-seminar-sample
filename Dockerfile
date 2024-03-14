FROM python:3.11

# 環境変数
ENV APP_PATH /opt/apps/server


# パッケージインストール
RUN apt-get update \
 && apt-get install -y --no-install-recommends binutils \
 && pip install poetry dumb-init \
 && poetry config virtualenvs.create false \
 && apt-get -y clean \
 && rm -rf /var/lib/apt/lists/*


# dumb-init を使う https://qiita.com/kojiwell/items/e8ac167671e331e9b050
ENTRYPOINT ["dumb-init"]


# パスの準備
RUN mkdir -p $APP_PATH
WORKDIR $APP_PATH


# 必要なパッケージのインストール
COPY ./pyproject.toml ./
COPY ./poetry.lock ./
RUN poetry install
