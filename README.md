# LauncherServer
オープンキャンパス/高専祭用のゲームランチャー用のサーバ\
[ゲームランチャー](https://github.com/pepi-p/GameLauncher)と組み合わせての使用を想定

# 導入
pythonで開発しているため，venvで環境を立て，srcに移動後，
以下のコマンドを実行するとサーバを立てられる

```
uvicorn main:app --host 0.0.0.0 --port 8000
```

hostとportは適切に設定すること．

[Releases](https://github.com/pepi-p/GameLauncher/releases)に，
batファイルが置いてある．
venv立てて，cloneしてきて，pip installして，と一連の流れを行う．
run.batはhostとportの指定がされていないため，各自で設定願う．
