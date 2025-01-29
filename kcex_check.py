import smtplib
import requests
import re
import os
from email.mime.text import MIMEText

# KCEX 上币信息页面（真实链接）
URL = "https://support.kcexhelp.com/hc/zh-tw/categories/25312022640409-%E4%B8%8A%E5%B9%A3%E4%BF%A1%E6%81%AF"

# 从 GitHub Secrets 读取邮件配置信息
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.qq.com")  # SMTP 服务器
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))  # 465 (SSL) 或 587 (TLS)
SENDER_EMAIL = os.getenv("SENDER_EMAIL")  # 发送方邮箱
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")  # SMTP 授权码
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")  # 接收方邮箱

# 爬取 KCEX 上币公告
def get_latest_kcex_news():
    try:
        response = requests.get(URL)
        response.raise_for_status()  # 确保请求成功
        content = response.text

        # 使用正则匹配公告标题和链接
        matches = re.findall(r'<a href="(\/hc\/zh-tw\/articles\/\d+-.*?)".*?>(.*?)<\/a>', content)

        if matches:
            latest_link, latest_title = matches[0]
            latest_link = "https://support.kcexhelp.com" + latest_link
            return latest_title, latest_link
    except requests.RequestException as e:
        print(f"❌ 请求 KCEX 页面失败: {e}")
    return None, None

# 发送邮件
def send_email(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject

    try:
        print("🔄 正在连接 SMTP 服务器...")
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("✅ 邮件发送成功！")
    except smtplib.SMTPException as e:
        print(f"❌ SMTP 发送失败: {e}")
    finally:
        try:
            server.quit()
        except:
            pass  # 避免 quit() 时报错

# 主函数
def main():
    latest_title, latest_link = get_latest_kcex_news()

    if latest_title:
        try:
            with open("last_kcex.txt", "r") as f:
                last_title = f.read().strip()
        except FileNotFoundError:
            last_title = ""

        if latest_title != last_title:
            with open("last_kcex.txt", "w") as f:
                f.write(latest_title)

            subject = f"KCEX 新上币公告：{latest_title}"
            body = f"新公告：{latest_title}\n查看详情：{latest_link}"
            send_email(subject, body)
            print("📧 邮件已发送！")
        else:
            print("✅ 没有新公告，无需发送邮件。")
    else:
        print("❌ 未能获取公告信息。")

if __name__ == "__main__":
    main()
