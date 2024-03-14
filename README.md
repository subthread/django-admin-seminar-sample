Django admin勉強会サンプル
==========================

### Docker環境の起動と終了

* すべて seminar-sample ディレクトリの中でコマンドラインから行う

* 初期化実行するとき：`make initialize`
    * 日々の活動のサンプルデータを登録するとき：`docker compose exec server python src/manage.py samplesummary`
* （初期化時以外で）Docker環境を起動するとき：`make`
* ローカル環境にアクセスするとき： http://localhost/
    * スーパーユーザーログイン情報
        * ユーザー名：`admin`
        * パスワード：`Admin123`
* Docker環境を終わらせるとき：control + C
* クリーンアップする（すべて消す）とき：`make clean`
    * `make initialize` すると内部で `make clean` も呼ばれる

### Googleログイン

* Googleログインを試す場合は次の手順を行う
    1. https://console.cloud.google.com/apis/credentials でクライアントIDを発行する
    2. seminar-sample/.env（無い場合は seminar-sample/default.env をコピーして作る）をテキストエディタで編集する
        * `GOOGLE_OAUTH_CLIENT_ID` と `GOOGLE_OAUTH_CLIENT_SECRET` に 1. で発行したクライアントIDとそれに紐づくシークレットを登録する
