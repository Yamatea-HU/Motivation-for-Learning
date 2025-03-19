import streamlit as st
import pandas as pd
import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheetsの設定
SHEET_ID = "1cy85MzRSUbLuGE5RarA-p2MdZ1AGRp-HbVMKWYaezck"
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Renderの環境変数 `GOOGLE_CREDENTIALS` からJSONキーを取得
creds_json = os.getenv("GOOGLE_CREDENTIALS")

if creds_json:
    try:
        creds_dict = json.loads(creds_json)  # JSON文字列を辞書に変換
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)  # 直接辞書から認証
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).sheet1
        st.success("Google Sheets に接続成功！")  # 接続成功時のメッセージ
    except Exception as e:
        st.error(f"Google Sheets APIの認証に失敗しました: {e}")  # 失敗した場合、詳細なエラーメッセージを表示
        st.text("環境変数 `GOOGLE_CREDENTIALS` の値が正しいか、Google Sheets の共有設定が適切か確認してください。")
else:
    st.error("Google Sheets APIの認証情報が環境変数 `GOOGLE_CREDENTIALS` に見つかりません！")
    st.text("Render の Environment タブで `GOOGLE_CREDENTIALS` の設定を確認してください。")

# タイトル
st.title("承認欲求尺度")

# 質問リスト
questions = [
    "1. 私は、人を喜ばせるために、自分の意見や行動を変える",
    "2. 私は、人とうまくやったり好かれるために、人が望むように振る舞おうとする傾向がある",
    "3.私は、励ましがなければ自分の仕事を続けることが困難である",
    "4.私は、自分の考えがグループの意見と異なるとき、自分の考えを言いにくい",
    "5.私は、友人が自分を支持してくれることがわかっているときだけ、すすんで議論に加わる",  
    "6.私は、人から良く思われるために自分を変えようとは思わない", # 逆転項目
    "7.私は、自分の進む道を必ずしも自分で決めていないと思うことが、時々ある",
    "8.私は、パーティーのような社交の場では、他人の嫌がることをしたり、言ったりしないように注意している",
    "9.私は、自分の行動を弁解したり、謝罪する必要があると感じることはめったにない",  # 逆転項目
    "10.私にとって、人との様々な交流の中で、“上手に”振舞うことは重要ではない",  # 逆転項目
    "11.私はたいてい、人が反対しても自分の立場を変えない",  # 逆転項目
    "12.重要人物に取り入るのは賢明である",
    "13.どれほどよい人間かで、友人の数が決まる",
    "14.最もうまい人の扱い方は、相手の考えに同意したり、相手の喜ぶようなことを言うことである",
    "15.たとえ自分のほうが正しいとわかっていても、他人からみれば間違っていると思われるようなことは、人前ですべきではない",
    "16.人と接するときは、積極的であるより控えめなほうがよい", 
    "17.私は、同じ状況であっても、相手が違えば異なる行動をとる",
    "18.誰かが私のことをあまり良く思っていないことがわかったら、次にその人に会ったとき、印象を良くするためにできるだけのことをする",
    "19.私に対してどんな批判があろうと、私はそれを受け入れることができる",
    "20.私は、どうすべきかをサイコロで決めたいと思うことがよくある"
]

# 逆転項目のインデックス（0始まり）
reverse_indices = [6, 9, 10, 11]  # 逆転する質問のインデックス

# 回答オプション
options = {
    "全くあてはまらない": 1,
    "あまりあてはまらない": 2,
    "ややあてはまる": 3,
    "わりとあてはまる": 4,
    "非常にあてはまる": 5
}

# ユーザーの回答を保存
responses = []

# 質問を表示
for i, question in enumerate(questions):
    response = st.radio(question, list(options.keys()), index=2)  # デフォルト: どちらでもない
    score = options[response]

    # 逆転項目ならスコアを変換
    if i in reverse_indices:
        score = 6 - score  # 1 ⇄ 5, 2 ⇄ 4, 3 はそのまま

    responses.append(score)

# 合計点を計算
if st.button("送信"):
    total_score = sum(responses)
    st.write(f"あなたの合計スコア: **{total_score} 点**")

    # Google Sheets にデータを保存
    if creds_json:
        try:
            row = [total_score] + responses
            sheet.append_row(row)  # 回答をGoogle Sheetsに追加
            st.success("回答がGoogle Sheetsに保存されました！")
        except Exception as e:
            st.error(f"データの保存に失敗しました: {e}")
    else:
        st.error("認証情報が設定されていないため、データを保存できません。")
