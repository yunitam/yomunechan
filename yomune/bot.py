# coding=utf-8
import os
from discord.ext import commands
import traceback

# 自分のBotのアクセストークンに置き換えてください(環境変数で設定)
token = os.environ['DISCORD_BOT_TOKEN']

INITIAL_EXTENSIONS = [
    "Cogs.voicecog"
]


# クラスの定義
class MyBot(commands.Bot):
    # MyBotのコンストラクタ
    def __init__(self, command_prefix):
        # スーパークラスのコンストラクタに値を渡して実行。
        super().__init__(command_prefix)

        # INITIAL_EXTENSIONSに格納されている名前から、コグを読み込む。
        # エラーが発生した場合は、エラー内容を表示。
        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    # Botの準備完了時に呼び出されるイベント
    async def on_ready(self):
        # 起動したらターミナルにログイン通知が表示される
        print("ログインしました")
        print(self.user.name)
        print(self.user.id)
        print('------')


if __name__ == '__main__':
    bot = MyBot(command_prefix='!')
    bot.run(token)
