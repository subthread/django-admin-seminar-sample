FROM localstack/localstack:3

# パッケージインストール
RUN apt-get update \
 && apt-get install -y --no-install-recommends jq \
 && pip install aws-sam-cli dumb-init \
 && apt-get -y clean \
 && rm -rf /var/lib/apt/lists/*

# aws configure
RUN mkdir /root/.aws
COPY ./.localstack.config /root/.aws/config
COPY ./.localstack.credentials /root/.aws/credentials

# 環境変数
ENV LOCALSTACK_HOST localhost
ENV AWS_REGION us-east-1
# https://github.com/localstack/localstack/issues/9701

# dumb-init を使う https://qiita.com/kojiwell/items/e8ac167671e331e9b050
ENTRYPOINT ["dumb-init"]
CMD ["docker-entrypoint.sh"]
