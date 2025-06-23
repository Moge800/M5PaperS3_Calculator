# M5PaperS3電卓アプリの使用方法

このUSAGEドキュメントでは、M5PaperS3電卓アプリのインストール方法と使用方法について説明します。このプログラムはApache License 2.0の下で提供されています。

## 準備

1. [UIFlow2.0](https://flow.m5stack.com/)をブラウザで開きます
2. M5PaperS3デバイスをUSBケーブルでコンピュータに接続します
3. デバイスをDFUモードにします（リセットボタンを押しながらMモードボタンを押す）

## プロジェクトのインポート手順

1. UIFlow2.0画面右上の「+」ボタンをクリックして新規プロジェクトを作成します
2. デバイスタイプとして「M5Paper S3」を選択します
3. プロジェクト名を「Calculator」などとして入力します
4. 作成したプロジェクトが開いたら、左側のファイル一覧で右クリックし「ファイルをインポート」を選択します
5. このリポジトリから以下のファイルをアップロードします：
   - calculator.py
   - boot.py

## プログラムのデバイスへの転送

1. UIFlow2.0画面右上の「接続」ボタンをクリックします
2. 表示されたデバイス一覧からM5PaperS3を選択して接続します
3. 右上の「実行」ボタンをクリックしてプログラムをデバイスに転送します
4. 転送が完了すると、自動的に電卓アプリが起動します

## UIFlow2.0での編集

UIFlow2.0では、以下の2つの方法でコードを編集することができます：

### 1. ブロックプログラミングモード

1. 画面上部の「ブロック」タブをクリックします
2. 表示されたブロックを使用して電卓の機能を編集します
3. ボタンのデザインや配置を変更する場合は「UI」カテゴリのブロックを使用します

### 2. Pythonコードモード

1. 画面上部の「Python」タブをクリックします
2. calculator.pyのコードが表示されます
3. 必要に応じてコードを編集します

## カスタマイズのヒント

### ボタンのデザイン変更

```python
# ボタンの色を変更する例
if key in '0123456789.':
    bg_color = 0x00FFFF  # 数字ボタンを水色に変更
elif key in ['+', '-', '*', '/', '=']:
    bg_color = 0xFF0000  # 演算子ボタンを赤色に変更
else:
    bg_color = 0x00FF00  # その他のボタンを緑色に変更
```

### ディスプレイのカスタマイズ

```python
# 表示エリアのカスタマイズ例
def draw_display_area():
    """表示エリアを描画する関数"""
    # タイトルを表示
    M5.Lcd.setTextColor(0x0000FF, WHITE)  # 青色に変更
    M5.Lcd.setTextSize(3)  # フォントサイズを大きく
    M5.Lcd.drawString("カスタム電卓", 10, 10)
    
    # 表示エリア（結果表示部分）- 背景色を変更
    M5.Lcd.fillRoundRect(20, 50, 500, 80, 8, 0x000000)  # 黒背景
    M5.Lcd.drawRoundRect(20, 50, 500, 80, 8, 0x00FF00)  # 緑の枠
```

### 追加機能の実装例

```python
# メモリー機能の追加例（M+、M-、MR、MC）
memory_value = 0

def memory_function(action):
    global memory_value, display_text
    
    if action == "M+":  # メモリーに加算
        memory_value += float(display_text)
    elif action == "M-":  # メモリーから減算
        memory_value -= float(display_text)
    elif action == "MR":  # メモリー呼び出し
        display_text = str(memory_value)
        update_display()
    elif action == "MC":  # メモリークリア
        memory_value = 0
```

## トラブルシューティング

1. **デバイスが認識されない場合**：
   - USBケーブルが正しく接続されているか確認します
   - デバイスを再起動してDFUモードに入り直します

2. **プログラムが転送されない場合**：
   - ブラウザを更新して再度接続します
   - デバイスのファームウェアを最新にアップデートします

3. **ディスプレイが更新されない場合**：
   - `update_display()` 関数を呼び出して画面を更新します
   - タッチ入力がうまく動作しない場合は `empty_touch_buffer()` を呼び出します

4. **計算結果がおかしい場合**：
   - 演算処理のコードをデバッグします（`print`文を使用）

## 参考リンク

- [M5Stack公式ドキュメント](https://docs.m5stack.com/)
- [M5PaperS3製品ページ](https://shop.m5stack.com/)
- [MicroPython公式ドキュメント](https://micropython.org/doc/)
- [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0)

- [M5Stack公式サイト](https://m5stack.com/)
- [UIFlow2.0マニュアル](https://docs.m5stack.com/en/quick_start/m5paper_s3/uiflow_v2)
- [M5PaperS3技術仕様書](https://docs.m5stack.com/en/core/M5PaperS3)
