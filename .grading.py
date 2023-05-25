import os
import subprocess
import sys
from pathlib import Path, PurePath

# python-dotenvがインストールされていなければインストール
try:
    from dotenv import load_dotenv
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv

# .grading.py の絶対パスを取得
script_path = Path(__file__).resolve()
env_path = script_path.parent / '.env'

# .env ファイルを読み込む
load_dotenv(env_path)
# grading.py を実行
base_path = os.getenv('BASE_PATH')

# 引数からモデルのパスを取得
model_path = sys.argv[1] if len(sys.argv) > 1 else ''

# ノートブック自身のパスを取得
student_notebook_path = model_path.split('/')[-1]

result = subprocess.run(['python3', 'Autograding/grading.py', '--model', str(base_path) + str(model_path), '--student', str(student_notebook_path)], capture_output=True, text=True)

# 採点結果を表示
print(result.stdout)

# エラーメッセージを表示
print(result.stderr)
