# coding=utf-8
import os
import discord
import re
import asyncio
import random
import json
from decimal import Decimal, ROUND_HALF_EVEN
from datetime import datetime
from discord.channel import VoiceChannel
from pytz import timezone
from discord.ext import commands
from google.cloud import texttospeech
from google.oauth2 import service_account

# ボイスチャンネルID
voice = {}
# テキストチャンネルID
channel = {}
# 音声種別['ja-JP-Wavenet-A'：女性,'ja-JP-Wavenet-B'：女性,'ja-JP-Wavenet-C：男性','ja-JP-Wavenet-D'：男性]
voice_namelist = ['ja-JP-Wavenet-A', 'ja-JP-Wavenet-B', 'ja-JP-Wavenet-C', 'ja-JP-Wavenet-D']
voice_name = 'ja-JP-Wavenet-a'
# 音声速度[0.25 〜 4.0]の範囲
voice_rate = float(1.1)
# 音声種別ランダムフラグ
voice_rnd_flg = bool(False)

# Google認証情報
if os.path.exists(os.environ['GOOGLE_CREDENTIALS']):
    #Debug用
    credentials = service_account.Credentials.from_service_account_file(os.environ['GOOGLE_CREDENTIALS'])
else:
    #Heroku用
    credetials_file = json.loads(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    credentials = service_account.Credentials.from_service_account_info(credetials_file)

# Instantiates a client
client = texttospeech.TextToSpeechClient(credentials=credentials)


class VoiceCog(commands.Cog):
    # コンストラクタ
    def __init__(self, bot):
        self.bot = bot

    # コマンドの作成
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def pingvoice(self, ctx):
        await ctx.send('pongvoice!')

    @commands.command()
    # @commands.has_permissions(manage_guild=True)
    @commands.has_permissions(read_messages=True, send_messages=True)
    async def vsta(self, ctx):
        # メッセージ送信者がBotだった場合は無視する
        if ctx.author.bot:
            return
        if self.bot.user != ctx.author:
            global voice
            global channel

            guild_id = ctx.guild.id  # ギルドIDを取得
            vo_ch = ctx.author.voice  # 召喚した人が参加しているボイスチャンネルを取得

            # 召喚した人がボイスチャンネルにいた場合
            if not isinstance(vo_ch, type(None)):
                tch_notice = ''
                # 召喚された時、voiceに情報が残っている場合
                if guild_id in voice:
                    # ボイスチャンネル切断
                    await voice[guild_id].disconnect()
                    del voice[guild_id]
                if guild_id in channel:
                    tch_notice = str(ctx.guild.get_channel(channel[guild_id]).mention) + ' が既に読み上げられていたため、読み上げを一旦終了しました。'
                    del channel[guild_id]
                # ボイスチャンネル接続
                voice[guild_id] = await vo_ch.channel.connect()
                channel[guild_id] = ctx.channel.id
                if tch_notice == '':
                    result = str(ctx.channel.mention) + ' の読み上げを開始します。'
                else:
                    result = tch_notice + '\n' + str(ctx.channel.mention) + ' の読み上げを開始します。'
            else:
                result = 'ボイスチャンネルに入ってからコマンドを実行して下さい。'
            # メッセージ表示
            em = discord.Embed(title='ボイスチャンネル接続', description=result, colour=7506394)
            await ctx.send(embed=em)

    @commands.command()
    # @commands.has_permissions(manage_guild=True)
    @commands.has_permissions(read_messages=True, send_messages=True)
    async def vend(self, ctx):
        # メッセージ送信者がBotだった場合は無視する
        if ctx.author.bot:
            return
        if self.bot.user != ctx.author:
            global voice
            global channel
            guild_id = ctx.guild.id

            if guild_id in voice:
                # コマンドが、呼び出したチャンネルで叩かれている場合
                if ctx.channel.id == channel[guild_id]:
                    # ボイスチャンネル切断
                    await voice[guild_id].disconnect()
                    # 情報を削除
                    if guild_id in voice:
                        del voice[guild_id]
                    if guild_id in channel:
                        del channel[guild_id]
                    # メッセージ表示
                    result = str(ctx.channel.mention) + ' の読み上げを終了しました。'
                else:
                    result = '【エラー】'
                    result += '\n' + str(ctx.channel.mention) + ' では、現在読み上げが開始されていないため、無効です。'
            else:
                result = '【エラー】'
                result += '\n' +  str(self.bot.user.display_name) + 'が接続しているボイスチャンネルを認識できません。'
                result += '\n何らかの問題で' + str(self.bot.user.display_name) + 'がボイスチャンネルに接続されたままの場合、強制切断コマンド[' + self.bot.command_prefix + 'vendforce]を入力して強制切断して下さい。'
            em = discord.Embed(title='ボイスチャンネル切断', description=result, colour=7506394)
            await ctx.send(embed=em)

    @commands.command()
    # @commands.has_permissions(manage_guild=True)
    @commands.has_permissions(read_messages=True, send_messages=True)
    async def vendforce(self, ctx):
        # メッセージ送信者がBotだった場合は無視する
        if ctx.author.bot:
            return
        if self.bot.user != ctx.author:
            global voice
            global channel
            guild_id = ctx.guild.id
            voice_client = ctx.message.guild.voice_client

            if not voice_client:
                result = '【エラー】'
                result += '\n' +  str(self.bot.user.display_name) + 'はボイスチャンネルに接続していません。'
            else:
                # 強制切断
                await voice_client.disconnect()
                # 情報を削除
                if guild_id in voice:
                    del voice[guild_id]
                if guild_id in channel:
                    del channel[guild_id]
                result = str(self.bot.user.display_name) + 'をボイスチャンネルから強制切断しました。'
            em = discord.Embed(title='ボイスチャンネル強制切断', description=result, colour=7506394)
            await ctx.send(embed=em)

    @commands.command()
    # @commands.has_permissions(manage_guild=True)
    @commands.has_permissions(read_messages=True, send_messages=True)
    async def vstop(self, ctx):
        # メッセージ送信者がBotだった場合は無視する
        if ctx.author.bot:
            return
        if self.bot.user != ctx.author:
            # ボイスチャンネルオブジェクトを取得
            voice_client = ctx.message.guild.voice_client
            if not isinstance(voice_client, type(None)):
                # 読み上げ停止
                if voice_client.is_playing():
                    voice_client.stop()
                    result = '読み上げ中の音声を停止しました。'
                    em = discord.Embed(title='読み上げ停止', description=result, colour=7506394)
                    await ctx.send(embed=em)

    @commands.command()
    # @commands.has_permissions(manage_guild=True)
    @commands.has_permissions(read_messages=True, send_messages=True)
    async def vspd(self, ctx, arg: str):
        # メッセージ送信者がBotだった場合は無視する
        if ctx.author.bot:
            return
        if self.bot.user != ctx.author:
            global voice_rate
            # 変更前の速度を取得
            bef_voice_rate = voice_rate
            # 正規表現で、0～4の整数または、0.0～4.99...までの数値かを判定
            p = re.compile(r'[0-4]+(\.[0-9]*)?')
            if p.fullmatch(arg):
                round_rate = Decimal(str(arg)).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)
                if 0.25 <= round_rate <= 4.0:
                    voice_rate = float(round_rate)
                    result = '設定を [' + str(bef_voice_rate) + '] から [' + str(voice_rate) + '] に変更しました。'
                else:
                    result = '設定値は [0.25～4.0] の範囲で指定して下さい。'
            else:
                result = '指定された設定値 [' + arg + '] は不正です。'
                result += '\n設定値は [0.25～4.0] の範囲で指定して下さい。'
            # メッセージ表示
            em = discord.Embed(title='読み上げ速度設定', description=result, colour=7506394)
            await ctx.send(embed=em)

    @commands.command()
    # @commands.has_permissions(manage_guild=True)
    @commands.has_permissions(read_messages=True, send_messages=True)
    async def vkind(self, ctx, arg: str):
        # メッセージ送信者がBotだった場合は無視する
        if ctx.author.bot:
            return
        if self.bot.user != ctx.author:
            global voice_name
            global voice_rnd_flg
            # 変更前の音声種別を取得
            bef_voice_name = voice_name
            if arg == 'a':
                # 女性音声
                voice_name = 'ja-JP-Wavenet-A'
            elif arg == 'b':
                # 女性音声
                voice_name = 'ja-JP-Wavenet-B'
            elif arg == 'c':
                # 男性音声
                voice_name = 'ja-JP-Wavenet-C'
            elif arg == 'd':
                # 男性音声
                voice_name = 'ja-JP-Wavenet-D'
            else:
                result = '指定された設定値 [' + arg + '] は不正です。'
                result += '\n設定値は [a] [b] [c] [d] のいずれかを指定して下さい。'
                em = discord.Embed(title='読み上げ音声設定', description=result, colour=7506394)
                await ctx.send(embed=em)
                return
            # 音声種別ランダムフラグがTrueの場合は、Falseに変更
            if voice_rnd_flg:
                voice_rnd_flg = False
            # メッセージ表示
            if bef_voice_name == voice_name:
                # 変更前と同じ場合
                result = '現在の設定 [' + str(bef_voice_name) + '] と同じです。'
            else:
                result = '設定を [' + str(bef_voice_name) + '] から [' + str(voice_name) + '] に変更しました。'
            result += '\n※音声のランダム化は自動的に無効になっています。'
            result += '\n※再度、音声のランダム化を行う場合は、[' + self.bot.command_prefix + 'vrnd] コマンドを実行して下さい。'
            em = discord.Embed(title='読み上げ音声設定', description=result, colour=7506394)
            await ctx.send(embed=em)

    @commands.command()
    # @commands.has_permissions(manage_guild=True)
    @commands.has_permissions(read_messages=True, send_messages=True)
    async def vrnd(self, ctx):
        # メッセージ送信者がBotだった場合は無視する
        if ctx.author.bot:
            return
        if self.bot.user != ctx.author:
            global voice_rnd_flg
            if voice_rnd_flg:
                voice_rnd_flg = False
                result = '設定を [無効(' + str(voice_rnd_flg) + ')] に変更しました。'
                result += '\n音声を変更したい場合は、 [' + self.bot.command_prefix + 'vkind] コマンドで設定して下さい。'
            else:
                voice_rnd_flg = True
                result = '設定を [有効(' + str(voice_rnd_flg) + ')] に変更しました。'
            # メッセージ表示
            em = discord.Embed(title='読み上げ音声ランダム化', description=result, colour=7506394)
            await ctx.send(embed=em)

    @commands.command()
    # @commands.has_permissions(manage_guild=True)
    @commands.has_permissions(read_messages=True, send_messages=True)
    async def vshow(self, ctx):
        # メッセージ送信者がBotだった場合は無視する
        if ctx.author.bot:
            return
        if self.bot.user != ctx.author:
            global voice_name
            global voice_rate
            global voice_rnd_flg
            # 設定内容表示
            em = discord.Embed(title='読み上げ設定表示', description='現在の設定内容はこちらです♪', colour=7506394)
            em.add_field(name='読み上げ音声', value=voice_name, inline=True)
            em.add_field(name='読み上げ速度', value=str(voice_rate), inline=True)
            em.add_field(name='音声ランダム化', value=str(voice_rnd_flg), inline=False)
            await ctx.send(embed=em)

    @commands.command()
    # @commands.has_permissions(manage_guild=True)
    @commands.has_permissions(read_messages=True, send_messages=True)
    async def vhelp(self, ctx):
        # メッセージ送信者がBotだった場合は無視する
        if ctx.author.bot:
            return
        if self.bot.user != ctx.author:
            # ヘルプ表示
            result = '各コマンドの説明はこちらです♪'
            result += '\nなお、下記のコマンドで変更可能な[読み上げ音声][読み上げ速度][音声ランダム化]は、サーバ内で共通です。'
            result += '\n個人ごとの設定はできません。'
            em = discord.Embed(title='読み上げコマンドヘルプ', description=result, colour=7506394)
            result = 'コマンドを実行したテキストチャンネルの読み上げを開始します。'
            result += '\nあなたが参加しているボイスチャンネルに「' + str(self.bot.user.display_name) + '」が参加しますので、あらかじめボイスチャンネルに参加した状態で、このコマンドを実行してください。'
            em.add_field(name=self.bot.command_prefix + 'vsta', value=result, inline=False)
            result = 'テキストチャンネルの読み上げを終了します。'
            result += '\nボイスチャンネルから全員が退出した場合は、自動的に読み上げを終了します。'
            em.add_field(name=self.bot.command_prefix + 'vend', value=result, inline=False)
            result = 'ボイスチャンネルから「' + str(self.bot.user.display_name) + '」を強制切断します。'
            result += '\n何らかの問題で「' + str(self.bot.user.display_name) + '」がボイスチャンネルに残ってしまったままの場合にご利用下さい。'
            result += '\n当コマンドでも切断できない場合は、管理者の対応をお待ち下さい。'
            em.add_field(name=self.bot.command_prefix + 'vendforce', value=result, inline=False)
            result = '読み上げ中の音声を停止します。'
            em.add_field(name=self.bot.command_prefix + 'vstop', value=result, inline=False)
            result = '読み上げ速度を変更します。'
            result += '\n現実的に聞き取りやすいのは、[1.0～1.5] の範囲です。'
            result += '\n入力例：' + self.bot.command_prefix + 'vspd　1.2'
            em.add_field(name=self.bot.command_prefix + 'vspd [引数=0.25～4.0の数値]', value=result, inline=False)
            result = '読み上げ音声を変更します。[a] [b] が女性の声、[c] [d] が男性の声です。'
            result += '\nコマンドを実行すると[音声のランダム化]は自動的に無効(False)に変更されます。'
            result += '\n入力例：' + self.bot.command_prefix + 'vkind　b'
            em.add_field(name=self.bot.command_prefix + 'vkind [引数=a, b, c, d のいずれかを指定]', value=result, inline=False)
            result = '読み上げ音声のランダム化設定を変更します。'
            result += '\nコマンドを実行する度に、有効(True)／無効(False)が切り替わります。'
            result += '\n有効にした場合、[' + self.bot.command_prefix + 'vkind] コマンドで指定可能な4種類の音声からランダムで再生されるようになります。'
            em.add_field(name=self.bot.command_prefix + 'vrnd', value=result, inline=False)
            result = '現在の読み上げの設定状況を表示します。'
            result += '\n表示対象は、[読み上げ音声][読み上げ速度][音声ランダム化]です。'
            em.add_field(name=self.bot.command_prefix + 'vshow', value=result, inline=False)
            await ctx.send(embed=em)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        global voice
        global channel
        guild_id = member.guild.id

        # 同じチャンネル内での変化（マイクミュートなど）の場合
        if before.channel == after.channel:
            pass  # 無視
        else:
            # 切断の場合
            if after.channel is None:
                # print(str(voice))
                if guild_id in voice:
                    # 1人しかボイスチャンネルに残っていない場合
                    if len(voice[guild_id].channel.members) == 1:
                        #名前がBot名と一致した場合
                        if voice[guild_id].channel.members[0].name == self.bot.user.name:
                            # ボイスチャンネル切断
                            await voice[guild_id].disconnect()
                            del voice[guild_id]
                            # メッセージ表示
                            result = str(self.bot.get_channel(channel[guild_id]).mention) + ' の読み上げを終了しました。'
                            em = discord.Embed(title='ボイスチャンネル自動切断', description=result, colour=7506394)
                            await self.bot.get_channel(channel[guild_id]).send(embed=em)
                            # 情報を削除
                            del channel[guild_id]

    @commands.Cog.listener()
    async def on_message(self, message):
        # メッセージ送信者がBotだった場合は無視する
        if message.author.bot:
            return
        # コマンドだった場合
        if message.content.startswith(self.bot.command_prefix):
            return
        global voice
        global channel
        global voice_namelist
        global voice_name
        global voice_rate
        global voice_rnd_flg
        # ギルドIDがない場合、DMと判断する
        if isinstance(message.guild, type(None)):
            return
        # ギルドID
        guild_id = message.guild.id
        # 召喚されていなかった場合
        if guild_id not in channel:
            return
        # メッセージを、呼び出されたチャンネルで受信した場合
        if message.channel.id == channel[guild_id]:
            # URLを、'URL'へ置換
            get_msg = re.sub(r'http(s)?://([\w-]+\.)+[\w-]+(/[-\w ./?%&=]*)?', 'URL省略', message.content)
            # reactionの置換
            get_msg = get_msg.replace('<:', '')
            get_msg = re.sub(r':[0-9]*>', '', get_msg)
            # mention と channel_mentionを名前へ置換
            mn_list = message.raw_mentions
            ch_list = message.raw_channel_mentions
            # IDに対応する名前の辞書を作成
            mn_dict = {}
            ch_dict = {}
            # mentionの、ユーザネームへの置換
            for ment in mn_list:
                mn_dict['<@!{}>'.format(str(ment))] = message.guild.get_member(ment).display_name
            # channel_mentionの、チャンネル名への置換
            for cnls in ch_list:
                ch_dict['<#{}>'.format(str(cnls))] = message.guild.get_channel(cnls).name
            # 変換テーブルの作成
            for me_key in mn_dict.keys():
                get_msg = get_msg.replace(me_key, mn_dict[me_key], 1)
            for ch_key in ch_dict.keys():
                get_msg = get_msg.replace(ch_key, ch_dict[ch_key], 1)
            # 個別置換
            # 空白
            get_msg = re.sub(r'[ｗwＷW]+[ 　]*', '、わら、', get_msg)
            get_msg = re.sub(r'[＠@]+[ 　]*', '、あっと、', get_msg)
            # 行末
            get_msg = re.sub(r'[ｗwＷW]$', '、わら、', get_msg)
            get_msg = re.sub(r'[＠@]$', '、あっと、', get_msg)
            # 改行
            get_msg = re.sub(r'[＠@]+[\r|\n\r\|\n]', '、あっと、', get_msg)
            # 半角、全角スペース
            get_msg = re.sub(r'[ 　]', '、', get_msg)
            # デバッグ用に置換後の文字列を出力
            #print(get_msg)
            # エラーメッセージ初期化
            result = ''
            # 200文字を超える場合は読み上げない
            if len(get_msg) > 200:
                result = '200文字を超えるため、読み上げません。'
            else:
                # ファイル名生成
                now = datetime.now(timezone('Asia/Tokyo'))
                filename = '../tmp/' + now.strftime('%Y-%m-%d_%H%M%S.mp3')
                # メッセージを、音声ファイルを作成するモジュールへ投げる処理
                try:
                    # Set the text input to be synthesized
                    synthesis_input = texttospeech.SynthesisInput(text=get_msg)
                    # 音声種別ランダムフラグがTrueの場合は、リストをシャッフル
                    if voice_rnd_flg:
                        random.shuffle(voice_namelist)
                        # シャッフル後の要素[0]を使用
                        voice_name = voice_namelist[0]
                    # Build the voice request, select the language code ('ja-JP') and the ssml
                    # voice gender ('NEUTRAL')
                    voice_param = texttospeech.VoiceSelectionParams(
                        language_code='ja-JP',
                        name=voice_name,
                        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
                    # Select the type of audio file you want returned
                    audio_config = texttospeech.AudioConfig(
                        audio_encoding=texttospeech.AudioEncoding.MP3,
                        speaking_rate=voice_rate)
                    # Perform the text-to-speech request on the text input with the selected
                    # voice parameters and audio file type
                    response = client.synthesize_speech(input=synthesis_input,
                                                        voice=voice_param,
                                                        audio_config=audio_config)
                    # The response's audio_content is binary.
                    with open(filename, 'wb') as out:
                        out.write(response.audio_content)
                # 失敗した場合
                except Exception as e:
                    result = '音声ファイルの作成でエラーが発生しました。\n' + str(e)
                try:
                    # 音声ファイルを再生中の場合再生終了まで待機
                    while message.guild.voice_client.is_playing():
                        # 他の処理をさせて1秒待機
                        await asyncio.sleep(1)
                    # ボイスチャンネルで再生
                    message.guild.voice_client.play(discord.FFmpegPCMAudio(filename))
                    await asyncio.sleep(0.5)
                except Exception as e:
                    result = '音声ファイルの再生でエラーが発生しました。\n' + str(e)
                finally:
                    # 音声ファイルを再生中の場合再生終了まで待機
                    while message.guild.voice_client.is_playing():
                        # 他の処理をさせて1秒待機
                        await asyncio.sleep(1)
            # エラー表示
            if result != '':
                em = discord.Embed(title='読み上げ処理エラー', description=result, colour=7506394)
                await message.channel.send(embed=em)


# Bot本体側からコグを読み込む際に呼び出される関数
def setup(bot):
    # VoiceCogにBotを渡してインスタンス化し、Botにコグとして登録する
    bot.add_cog(VoiceCog(bot))
