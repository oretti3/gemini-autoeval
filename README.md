# 自動評価スクリプト(Gemini対応)

評価者のLLMを指定して、言語モデルの応答を自動評価するスクリプト。  
評価者にGemini 1.5 Proを追加し、無料で評価可能にしました。

## 対応する言語モデル

評価者のLLMとして、下記のモデルを選択できる。  
モデル名は `JUDGE` 環境変数で指定する。

* `google/gemini-pro`: Google Gemini 1.5 Pro API
* `openai/gpt-4`: OpenAI GPT-4 Turbo API
* `openai/gpt-4o`: OpenAI GPT-4o API
* `cohere/command-r-plus`: Cohere Command-R+ API

## 使用方法

### LLM によるテキスト生成

#### 方法1
`notebooks` ディレクトリ配下にあるノートブックを実行することで、評価対象のLLMに ELYZA-tasks-100 データセットの各質問に対する回答が生成できる。  
ノートブックは、[Google Colaboratory](https://colab.research.google.com/) などで実行可能。  
  
生成されたテキストは `preds.jsonl` という名前の JSONL ファイルに書き出される。
このファイルをダウンロードする。  

#### 方法2
`tools`ディレクトリ配下にある`generation.py`を実行することで、データセットの各質問に対する回答が生成できる。
生成されたテキストは `assets/{指定データセット}/preds.jsonl` という名前の JSONL ファイルに書き出される。

```console
$ cd tools/docker/win-autoeval-tools
$ docker compose up -d
$ docker compose exec app bash
$ python generation.py
```

### 評価の準備

下記のように、`assets/<DATASET_NAME>` にデータセット・LLMの応答を JSONL 形式で配置する。  
（フォーマットの詳細は `assets/test` を参照）

`dataset.jsonl` は `assets/elyza_tasks_100` からハードリンク（またはコピー）する。

```
assets/<DATASET_NAME>/
 - dataset.jsonl
 - preds.jsonl
```

### 評価

#### Gemini を使う場合

Gemini API キーを発行し ([link](https://makersuite.google.com/app/prompts/new_freeform))、 `secrets/GEMINI_API_KEY` に置く (行末は**改行しない**)。

```console
$ touch secrets/GEMINI_API_KEY
$ echo "your_api_key" > ./secrets/GEMINI_API_KEY
```
その後、下記コマンドを実行する。

```console
$ DATASET_NAME=elyza_tasks_100 JUDGE=google/gemini-pro docker compose up --build
```

評価結果は JSONL 形式で `assets/elyza_tasks_100/result.jsonl` に保存される。


#### GPT-4 を使う場合

OpenAI API キーを発行し ([link](https://platform.openai.com/api-keys))、 `secrets/OPENAI_API_KEY` に置く (行末は**改行しない**)。

```console
$ cat secrets/OPENAI_API_KEY
my-OPeNAiKeY...
```

評価方法は、下記の2通りから選択できる。

* **`sequential` モード**（デフォルト）: LLMの応答を1つずつ OpenAI API に送信し、評価する。評価結果は、標準出力に順次表示される。
* **`batch` モード**: OpenAI API の[バッチ推論機能](https://platform.openai.com/docs/api-reference/batch) を使用する。結果は 24 時間以内に返却される。API利用料が割安。

##### `sequential` モード

```console
$ DATASET_NAME=<DATASET_NAME> JUDGE=openai/gpt-4o docker compose up --build
```

評価結果は JSONL 形式で `assets/<DATASET_NAME>/result.jsonl` に保存される。

##### `batch` モード

バッチ推論ジョブを作成する。

```console
$ DATASET_NAME=<DATASET_NAME> PROCESS_MODE=batch BATCH_TASK=submit \
  JUDGE=openai/gpt-4o \
        docker compose up --build
```

ジョブIDが `assets/<DATASET_NAME>/batch_id.txt` に保存される。

ジョブの結果を取得する。

```console
$ DATASET_NAME=<DATASET_NAME> PROCESS_MODE=batch BATCH_TASK=retrieve \
        docker compose up --build
```

ジョブが未完了の場合は、その旨が表示される。

ジョブが完了した場合、評価結果は JSONL 形式で `assets/<DATASET_NAME>/result.jsonl` に保存される。

#### Cohere API を使う場合

Cohere API キーを発行し ([link](https://dashboard.cohere.com/api-keys))、 `secrets/COHERE_API_KEY` に置く (行末は**改行しない**)。

```console
$ cat secrets/COHERE_API_KEY
myCohereKey...
```

その後、下記コマンドを実行する。

```console
$ DATASET_NAME=<DATASET_NAME> JUDGE=cohere/command-r-plus docker compose up --build
```

評価結果は JSONL 形式で `assets/<DATASET_NAME>/result.jsonl` に保存される。

### スコアリング
`tools`ディレクトリ配下にある`scoring.py`を実行することで、スコア一覧が生成できる。
生成されたスコアは `assets/{指定データセット}/score.txt` という名前の テキストファイルに書き出される。

```console
$ cd tools/docker/win-autoeval-tools
$ docker compose up -d
$ docker compose exec app bash
$ python scoring.py
```
もしくは
```console
$ cd tools
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ python scoring.py
```


### 結果の一覧表示

Google スプレッドシートで結果を一覧表示する場合（[表示例](https://docs.google.com/spreadsheets/d/1nOWtneRdrkxwQbAN0rWmXqiJXR9IXK9lVkyDjQTqNGc/edit?usp=sharing)）は、 `<DATASET_NAME>/{preds,results}.jsonl` を Google Drive にコピーし、`tools/copy_jsonl_to_google_spreadsheet.js` を Google Apps Script として実行する。

## 環境変数一覧

| 変数名 | とりうる値 | デフォルト値 | 説明 |
| --- | --- | --- | --- |
| `DATASET_NAME` | - | - | データセット名。`assets/<DATASET_NAME>` にデータセットを配置する |
| `PROCESS_MODE` | `sequential`, `batch` | `sequential` | 評価モード。`batch` は OpenAI API のみ対応 |
| `JUDGE` | `google/gemini-pro`,`openai/gpt-4`, `openai/gpt-4o`, `cohere/command-r-plus` | `openai/gpt-4` | 評価者のLLM |
| `BATCH_TASK` | `submit`, `retrieve` | `submit` | バッチ推論のタスク。`PROCESS_MODE=batch` 以外のときは無視される |

## 動作環境

* WSL v2.0.14.0
* Docker Compose v2.24.7

## クレジット

* ELYZA-tasks-100: ELYZA (CC BY-SA 4.0), [link](https://huggingface.co/datasets/elyza/ELYZA-tasks-100)
* Northern-System-Service/gpt4-autoeval, [link](https://github.com/Northern-System-Service/gpt4-autoeval)
* umiyuki/Umievo-itr012-Gleipnir-7B , [link](https://huggingface.co/umiyuki/Umievo-itr012-Gleipnir-7B)

以上
