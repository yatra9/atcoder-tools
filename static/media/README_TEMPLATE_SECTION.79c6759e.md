テンプレートエンジンの仕様については[jinja2](http://jinja.pocoo.org/docs/2.10/) の公式ドキュメントを参照してください。

テンプレートに渡される変数は以下の通りです。


- **prediction_success** 入力形式の推論に成功したとき `True`、 失敗したとき `False`が格納されている。この値が`True`のとき次の3種類の変数も存在することが保証される。
    - **input_part** input用のコード
    - **formal_arguments** 型つき引数列
    - **actual_arguments** 型なし引数列

- **mod** 問題文中に存在するmodの整数値
- **yes_str** 問題文中に存在する yes や possible などの真を表しそうな文字列値
- **no_str** 問題文中に存在する no や impossible などの偽を表しそうな文字列値


