# 1. Pythonの環境を借りてくる
FROM python:3.9-slim

# 2. コンテナの中の作業場所を決める
WORKDIR /app

# 3. 必要なライブラリをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 自分のコードをコンテナの中にコピー
COPY app.py .

# 5. アプリを起動するコマンドを指定
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]