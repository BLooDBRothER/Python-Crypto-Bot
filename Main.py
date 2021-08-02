#!/usr/bin/env python3

import apikey
import db
import telebot
from telebot import types
from telebot import util
from binance.client import Client
import datetime
import time
import requests
import json
import random
import qrcode
from PIL import Image
import pyotp

bot = telebot.TeleBot(apikey.tkey, parse_mode="HTML")

client = Client(apikey.key, apikey.skey)

btc_price = client.get_symbol_ticker(symbol="BTCUSDT")

deg = u'\N{DEGREE SIGN}'

pair_lis = ['BTC', 'ETH', 'BNB', 'USDT']

command_lis = ['/start', '/greet', '/help', '/price',
               '/signup', '/login', '/movie', '/logout', '/mydata', '/2fa', '/2far', '/resetpass', '/update', '/weather', '/history', '/clrhis']

# --------------------- History ------------------------
def inshis(message, data):
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    if(not(datau == 0)):
        db.hisins(datau[0], data)

# ---------------------   START ------------------------

@bot.message_handler(commands=['start', 'help', 'greet'])
def send_welcome(message):
    inshis(message, "/start")
    x = datetime.datetime.now()
    dt = f"{x.strftime('%a  -  %b %d %Y  -  %I:%M:%S %P')}"
    pstr = f"<b>{dt}</b>\n\n\
	/signup to register"
    bot.send_message(message.chat.id, pstr)

# --------------------- Weather ------------------------
@bot.message_handler(commands=['weather'])
def wdata(message):
    msg = bot.send_message(message.chat.id, "Enter Pincode")
    inshis(message, "/weather")
    bot.register_next_step_handler(msg, wprint)

def wprint(message):
    url =  f"https://api.openweathermap.org/data/2.5/weather?zip={message.text},in&appid={apikey.owkey}&units=imperial"
    res = requests.get(url)
    if(res.status_code == 200 or res.status_code == 201):
        data = res.json()
        frm = f'Weather at <b><i><u>{data["name"]}</u></i></b>\n\n\
Temperature     - {data["main"]["temp"]}{deg}F\n\
Temperature Min - {data["main"]["temp_min"]}{deg}F\n\
Temperature Max - {data["main"]["temp_max"]}{deg}F\n\
Pressure        - {data["main"]["pressure"]}\n\
Humidity        - {data["main"]["humidity"]}\n\n\
<code>{data["weather"][0]["description"]}</code>'
        bot.send_message(message.chat.id, frm)
    else:
        bot.send_message(message.chat.id, "Invalid Input")

# --------------------- MOVIE ------------------------

@bot.message_handler(commands=['movie'])
def moviest(message):
    msg = bot.send_message(message.chat.id, "Enter movie or series name")
    inshis(message, "/movie")
    bot.register_next_step_handler(msg, movie)


def movie(message):
    if(not(message.content_type == 'text')):
        bot.send_message(
            message.chat.id, "<B><U><I>INVALID CREDENTIALS </I></U></B>")
        return
    url = f"http://www.omdbapi.com/?t={message.text}&apikey=a1e59ae"
    res = requests.get(url)
    text = res.text
    data = json.loads(text)
    res = data['Response']
    if(res == "False"):
        bot.send_message(message.chat.id, "Sorry no DATA")
        return

    iurl = f"https://www.imdb.com/title/{data['imdbID']}/"

    rstr = ''
    for i in data['Ratings']:
        if(i['Source'] == 'Internet Movie Database'):
            rstr += f"Source  -  <code>IMBD</code>\nValue   -  <code>{i['Value']}</code>\n\n"
        else:
            rstr += f"Source  -  <code>{i['Source']}</code>\nValue   -  <code>{i['Value']}</code>\n\n"

    str = f"Title :  <code>{data['Title']}</code>\n\n\
Released :  <code>{data['Released']}</code>\n\n\
Genre :  <code>{data['Genre']}</code>\n\n\
Director :  <code>{data['Director']}</code>\n\n\
Actors :  <code>{data['Actors']}</code>\n\n\
Awards :  <code>{data['Awards']}</code>\n\n\
Language :  <code>{data['Language']}</code>\n\n\
Rating :\n<code>{rstr}</code>\n\
IMBD LINK :  {iurl}"

    bot.send_message(message.chat.id, str)



# ------------------------------------------- SIGNUP ---------------------------------------


@bot.message_handler(commands=['signup'])
def signup(message):
    inshis(message, "/signup")
    if(db.checkdet(message.chat.id, "chatid")):
        print(message.chat.id)
        datas = db.lpcheck("status", message.chat.id, "chatid", "cuser")
        if(datas[0] == 'F'):
            datas = db.lpcheck("chatid", message.text, "uname", "cuser")
            db.deldet(message.chat.id, "cuser")
            db.deldet(message.chat.id, "service")
            signup(message)
        else:
            msg = bot.send_message(
                message.chat.id, "User Already exists do you want the User name associated with this Y/N")
            bot.register_next_step_handler(msg, suserre)
    else:
        db.inscid(message.chat.id, "chatid", "cuser")
        db.inscid(message.chat.id, "chatid", "service")
        msg = bot.send_message(message.chat.id, "Enter User Name: ")
        bot.register_next_step_handler(msg, spass)


def suserre(message):
    if(not(message.content_type == 'text') or (len(message.text) > 10)):
        bot.send_message(
            message.chat.id, "<B><U><I>INVALID CREDENTIALS </I></U></B>")
        return
    if(message.text.upper() == 'Y'):
        bot.send_message(message.chat.id, db.udetails(message.chat.id)[1])
    else:
        bot.send_message(message.chat.id, "Thank You Have A Nice Day")


def spass(message):
    if(not message.content_type == 'text' or (len(message.text) > 10)):
        bot.send_message(
            message.chat.id, "<B><U><I>INVALID CREDENTIALS </I></U></B>")
        db.deldet(message.chat.id, "cuser")
        db.deldet(message.chat.id, "service")
        return
    if(db.checkdet(message.text, "uname")):
        msg = bot.send_message(
            message.chat.id, "User Already Exists: \n\n Try Again")
        db.deldet(message.chat.id, "cuser")
        db.deldet(message.chat.id, "service")
    else:
        db.insdata(message.chat.id, "uname", message.text, "cuser")
        db.insdata(message.chat.id, "uname", message.text, "service")
        msg = bot.send_message(message.chat.id, "Enter Password: ")
        bot.register_next_step_handler(msg, sfav)


def sfav(message):
    if(not message.content_type == 'text' or len(message.text) > 10):
        bot.send_message(
            message.chat.id, "<B><U><I>INVALID CREDENTIALS </I></U></B>")
        db.deldet(message.chat.id, "cuser")
        db.deldet(message.chat.id, "service")
        return
    db.insdata(message.chat.id, "password", message.text, "cuser")
    msg = bot.send_message(message.chat.id, "Enter Your Favorite Coins\n\n\
For Pair coins  start with p - (pbtcusdt)\n\n\
Space separated or newline eg - (dodo coti preefusdt)")
    bot.register_next_step_handler(msg, supdate)


def supdate(message):
    if(not message.content_type == 'text'):
        bot.send_message(
            message.chat.id, "<B><U><I>INVALID CREDENTIALS </I></U></B>")
        db.deldet(message.chat.id, "cuser")
        return
    db.insdata(message.chat.id, "status", 'T', "cuser")
    db.insdata(message.chat.id, "favcoins", message.text, "service")
    bot.send_message(message.chat.id, "<b><i>/login to login. After login You can enable 2FA by /2fa</i></b>")

# ---------------------   LOGIN ------------------------


@bot.message_handler(commands=['login'])
def login(message):
    inshis(message, "/login")
    data = db.lcheck(message.chat.id)
    if(not data):
        msg = bot.send_message(message.chat.id, "Enter User Name ")
        db.inscid(message.chat.id, "chatid", "login")
        bot.register_next_step_handler(msg, lpass)
    else:
        datac = db.lpcheck("status", message.chat.id, "chatid", "login")
        if(datac[0] == 'F'):
            db.deldet(message.chat.id, "login")
            login(message)
        else:
            bot.send_message(
                message.chat.id, f"Already logged with User Name <code>{data[0]}</code>")


def lpass(message):
    if(not message.content_type == 'text' or len(message.text) > 10):
        bot.send_message(
            message.chat.id, "<B><U><I>INVALID CREDENTIALS </I></U></B>")
        db.deldet(message.chat.id, "login")
        return
    data = db.lpcheck("*", message.text, "uname", "cuser")
    if(data == 0):
        bot.send_message(
            message.chat.id, "<B><U><I>USER DOES NOT EXIST</I></U></B>")
        db.deldet(message.chat.id, "login")
    else:
        datac = db.lpcheck("chatid", message.text, "uname", "cuser")
        datas = db.lpcheck("status", datac[0], "chatid", "cuser")
        if(datas[0] == 'F'):
            db.deldet(datac[0], "cuser")
            db.deldet(datac[0], "service")
            bot.send_message(message.chat.id, "<B><U><I>USER DOES NOT EXIST</I></U></B>")
            return
        db.insdata(message.chat.id, "uname", message.text, "login")
        msg = bot.send_message(message.chat.id, "Enter Password ")
        bot.register_next_step_handler(msg, lpasscheck)


def lpasscheck(message):
    if(not message.content_type == 'text' or len(message.text) > 10):
        bot.send_message(
            message.chat.id, "<B><U><I>INVALID CREDENTIALS </I></U></B>")
        db.deldet(message.chat.id, "login")
        return
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    datap = db.lpcheck("password", datau[0], "uname", "cuser")
    if(datap[0] == message.text):
        datat = db.lpcheck("auth", datau[0], "uname", "cuser")
        db.insdata(message.chat.id, "status", 'T', "login")
        if(not(datat[0] == 'TOTP') and not(datat[0] == 'OTP')):
            bot.send_message(message.chat.id, "You have not Enabled 2FA /2fa to enable it. 2FA necessarry to delete or reset password")
        bot.send_message(message.chat.id, "Successfully Logged IN")
        print(datau)
        datalu =  db.logchat(datau[0])
        for i in datalu:
            for j in i:
                if(not(j == message.chat.id)):
                    bot.send_message(j, f"Login detected by <code>{message.chat.first_name+message.chat.last_name}</code>")
    else:
        bot.send_message(message.chat.id, "<B><U><I>INVALID PASSWORD</I></U></B>")
        db.deldet(message.chat.id, "login")

# --------------------- LOGOUT ------------------------


@bot.message_handler(commands=['logout'])
def logout(message):
    inshis(message, "/logout")
    if(not message.content_type == 'text' or len(message.text) > 10):
        bot.send_message(
            message.chat.id, "<B><U><I>INVALID CREDENTIALS </I></U></B>")
        return
    data = db.lpcheck("uname", message.chat.id, "chatid", "login")
    if(data == 0):
        bot.send_message(
            message.chat.id, "<B><U><I>You are not logged IN</I></U></B> /login to login or /signup to signup")
    else:
        msg = bot.send_message(
            message.chat.id, f"You are logged IN as <B><code><I>{data[0]}</I></code></B>\nEnter password to logout")
        bot.register_next_step_handler(msg, lout)


def lout(message):
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    datap = db.lpcheck("password", datau[0], "uname", "cuser")
    if(datap[0] == message.text):
        bot.send_message(message.chat.id, "Successfully Logged OUT")
        db.deldet(message.chat.id, "login")
    else:
        bot.send_message(
            message.chat.id, "<B><U><I>INVALID PASSWORD</I></U></B>")

# --------------------- Reset Password ------------------------

@bot.message_handler(commands=['resetpass'])
def passre(message):
    inshis(message, "/resetpass")
    if(not message.content_type == 'text' or len(message.text) > 10):
        bot.send_message(
            message.chat.id, "<B><U><I>INVALID CREDENTIALS </I></U></B>")
        return
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    if(datau == 0):
        bot.send_message(message.chat.id, "<B><U><I>You are not logged IN</I></U></B> /login to login or /signup to signup")
        return
    datac = db.lpcheck("status", message.chat.id, "chatid", "login")
    if(datac[0] == 'F'):
        db.deldet(message.chat.id, "login")
        bot.send_message(message.chat.id, "<B><U><I>You are not logged IN</I></U></B> /login to login or /signup to signup")
        return
    datat = db.lpcheck("auth", datau[0], "uname", "cuser")
    if(not(datat[0] == 'TOTP') and not(datat[0] == 'OTP')):
        bot.send_message(message.chat.id, "You have not Enabled 2FA /2fa to enable it. 2FA necessarry to delete or reset password")
        return
    datac = db.lpcheck("chatid", datau[0], "uname", "cuser")
    if(datat[0] == 'OTP'):
            otp = random.randint(1000, 9999)
            db.insdata(datac[0], "cotp", otp, "otp")
            bot.send_message(datac[0], f"otp for Changing Password {otp}")
            msg = bot.send_message(message.chat.id, "OTP sent successful")
            msg = bot.send_message(message.chat.id, "Enter OTP")
            bot.register_next_step_handler(msg, resotp)
    else:
            msg = bot.send_message(message.chat.id, "Enter TOTP")
            bot.register_next_step_handler(msg, restotp)

def resotp(message):
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    dataotp = db.lpcheck("cotp", datau[0], "uname", "otp")
    if(str(dataotp[0]) == message.text):
        msg = bot.send_message(message.chat.id, "Enter New Password")
        bot.register_next_step_handler(msg, resetpass)
    else:
        msg = bot.send_message(message.chat.id, "Enter OTP")
        bot.register_next_step_handler(msg, resotp)

def restotp(message):
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    dataotp = db.lpcheck("totp", datau[0], "uname", "otp")
    totp = pyotp.TOTP(dataotp[0])
    if(str(totp.now()) == message.text):
        msg = bot.send_message(message.chat.id, "Enter New Password")
        bot.register_next_step_handler(msg, resetpass)
    else:
        bot.send_message(message.chat.id, "<B><U><I>INVALID TOTP</I></U></B>")
        msg = bot.send_message(message.chat.id, "<B><U><I>ENTER TOTP</I></U></B>")
        bot.register_next_step_handler(msg, restotp)

def resetpass(message):
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    datac = db.lpcheck("chatid", datau[0], "uname", "cuser")
    db.insdata(datac[0], "password", message.text, "cuser")
    bot.send_message(message.chat.id, "<B><U><I>Password Reset Successful</I></U></B>")
    datalu =  db.logchat(datau[0])
    print(datalu)
    for i in datalu:
        for j in i:
            print(j)
            bot.send_message(j, "Password has been Reseted /login to login again")
            db.deldet(i, "login")


# --------------------- 2 FACTOR AUTHENTICATION ------------------------

@bot.message_handler(commands=['2fa'])
def f2in(message):
    inshis(message, "/2fa")
    data = db.lpcheck("uname", message.chat.id, "chatid", "login")
    if(data == 0):
        bot.send_message(message.chat.id, "<B><U><I>You are not logged IN</I></U></B> /login to login or /signup to signup")
        return
    datac = db.lpcheck("status", message.chat.id, "chatid", "login")
    if(datac[0] == 'F'):
        db.deldet(message.chat.id, "login")
        bot.send_message(message.chat.id, "<B><U><I>You are not logged IN</I></U></B> /login to login or /signup to signup")
        return
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    datat = db.lpcheck("auth", datau[0], "uname", "cuser")
    print(datau, datat)
    if(datat[0] == 'OTP' or datat[0] == 'TOTP'):
        bot.send_message(message.chat.id, "<B><U><I>You have already enabled 2 Factor authentication /2far to reset it</I></U></B>")
        return
    datac = db.lpcheck("chatid", datau[0], "uname", "cuser")
    chc = db.lpcheck("chatid", datac[0], "chatid", "otp")
    if(not (chc == 0)):
        db.deldet(datac[0], "otp")
    msg = bot.send_message(message.chat.id, "Enable 2FA\n\n1.chatid OTP\n\n2.Gauth\n\n<b><i>Note\nFor OTP current telegram id will be used to receive OTP</i></b>")
    bot.register_next_step_handler(msg, renb2f)

def renb2f(message):
    if(not message.content_type == 'text'):
        bot.send_message(message.chat.id, "<B><U><I>INVALID CREDENTIALS </I></U></B>")
        return
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    datac = db.lpcheck("chatid", datau[0], "uname", "cuser")
    print(datau, datac)
    if(message.text == '1'):
        otp = random.randint(1000, 9999)
        db.inscid(datac[0], "chatid", "otp")
        db.insdata(datac[0], "cotp", otp, "otp")
        db.insdata(datac[0], "uname", datau[0], "otp")
        bot.send_message(datac[0], f"otp for Enabling 2FA {otp}")
        msg = bot.send_message(message.chat.id, "OTP sent successful")
        msg = bot.send_message(message.chat.id, "Enter OTP")
        bot.register_next_step_handler(msg, cf2a)
    elif(message.text == '2'):
        f2a(message)

def cf2a(message):
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    datac = db.lpcheck("chatid", datau[0], "uname", "cuser")
    dataotp = db.lpcheck("cotp", datau[0], "uname", "otp")
    print(dataotp)
    if(str(dataotp[0]) == message.text):
        db.insdata(datac[0], "auth", "OTP", "cuser")
        bot.send_message(message.chat.id, "Enabled 2FA - OTP")
    else:
        msg = bot.send_message(message.chat.id, "Enter OTP")
        bot.register_next_step_handler(msg, chatotpcheck)

def f2a(message):
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    datac = db.lpcheck("chatid", datau[0], "uname", "cuser")
    print(datau, datac)
    rt = pyotp.random_base32()
    totp = pyotp.TOTP(rt)
    print(totp.now(), rt)
    tt = pyotp.totp.TOTP(rt).provisioning_uri(name=datau[0], issuer_name='Tele bot')
    db.toins(datac[0], datau[0], rt)
    img = qrcode.make(rt)
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=5, border=4,)
    qr.add_data(tt)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    bot.send_message(message.chat.id, f"TOTP CODE FOR {datau[0]}")
    bot.send_photo(message.chat.id, img, f"<code>{rt}</code>")
    msg = bot.send_message(message.chat.id, "<B><U><I>ENTER TOTP</I></U></B>")
    bot.register_next_step_handler(msg, tcheck)

def tcheck(message):
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    dataotp = db.lpcheck("totp", datau[0], "uname", "otp")
    datac = db.lpcheck("chatid", datau[0], "uname", "cuser")
    totp = pyotp.TOTP(dataotp[0])
    if(str(totp.now()) == message.text):
        db.insdata(datac[0], "auth", "TOTP", "cuser")
        bot.send_message(message.chat.id, "Enabled 2FA - OTP")
    else:
        msg = bot.send_message(message.chat.id, "<B><U><I>ENTER TOTP</I></U></B>")
        bot.register_next_step_handler(msg, tcheck)


@bot.message_handler(commands=['2far'])
def f2arc(message):
    inshis(message, "/2far")
    data = db.lpcheck("uname", message.chat.id, "chatid", "login")
    if(data == 0):
        bot.send_message(message.chat.id, "<B><U><I>You are not logged IN</I></U></B> /login to login or /signup to signup")
        return
    datac = db.lpcheck("status", message.chat.id, "chatid", "login")
    if(datac[0] == 'F'):
        db.deldet(message.chat.id, "login")
        bot.send_message(message.chat.id, "<B><U><I>You are not logged IN</I></U></B> /login to login or /signup to signup")
        return
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    datat = db.lpcheck("auth", datau[0], "uname", "cuser")
    if(not(datat[0] == 'OTP') and not(datat[0] == 'TOTP')):
        bot.send_message(message.chat.id, "<B><U><I>Enable</I></U></B> 2FA /2fa")
        return  
    msg = bot.send_message(message.chat.id, "1.Remove 2FA\n\n2.Change TOTP")
    bot.register_next_step_handler(msg, chfr)

def chfr(message):
    if(not message.content_type == 'text'):
        bot.send_message(message.chat.id, "<B><U><I>INVALID CREDENTIALS </I></U></B>")
        return
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    datat = db.lpcheck("auth", datau[0], "uname", "cuser")
    datac = db.lpcheck("chatid", datau[0], "uname", "cuser")
    if(message.text == '1'):
        print(datau, datat, datac)
        if(datat[0] == 'OTP'):
            otp = random.randint(1000, 9999)
            db.insdata(datac[0], "cotp", otp, "otp")
            bot.send_message(datac[0], f"otp for removing {otp}")
            msg = bot.send_message(message.chat.id, "OTP sent successful")
            msg = bot.send_message(message.chat.id, "Enter OTP")
            bot.register_next_step_handler(msg, chatotpcheck)
        else:
            msg = bot.send_message(message.chat.id, "Enter TOTP")
            bot.register_next_step_handler(msg, totpcheck)
    elif(message.text == '2'):
        if(datat[0] == 'OTP'):
            msg = bot.send_message(message.chat.id, "Invalid operation")
            return
        msg = bot.send_message(message.chat.id, "Enter TOTP")
        bot.register_next_step_handler(msg, retpcheck)
    else:
        bot.send_message(message.chat.id, "Invalid operation")

def chatotpcheck(message):
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    datac = db.lpcheck("chatid", datau[0], "uname", "cuser")
    dataotp = db.lpcheck("cotp", datau[0], "uname", "otp")
    print(datau, datac, dataotp)
    if(str(dataotp[0]) == message.text):
        db.insdata(datac[0], "auth", "disabled", "cuser")
        db.deldet(datac[0], "otp")
        bot.send_message(message.chat.id, "<B><U><I>2FA Deleted</I></U></B>")
    else:
        msg = bot.send_message(message.chat.id, "Enter OTP")
        bot.register_next_step_handler(msg, chatotpcheck)

def totpcheck(message):
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    datac = db.lpcheck("chatid", datau[0], "uname", "cuser")
    dataotp = db.lpcheck("totp", datau[0], "uname", "otp")
    totp = pyotp.TOTP(dataotp[0])
    if(str(totp.now()) == message.text):
        db.insdata(datac[0], "auth", "disabled", "cuser")
        db.deldet(datac[0], "otp")
        bot.send_message(message.chat.id, "<B><U><I>2FA Deleted</I></U></B>")
    else:
        bot.send_message(message.chat.id, "<B><U><I>INVALID TOTP</I></U></B>")
        msg = bot.send_message(message.chat.id, "<B><U><I>ENTER TOTP</I></U></B>")
        bot.register_next_step_handler(msg, totpcheck)

def retpcheck(message):
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    datac = db.lpcheck("chatid", datau[0], "uname", "cuser")
    dataotp = db.lpcheck("totp", datau[0], "uname", "otp")
    totp = pyotp.TOTP(dataotp[0])
    if(str(totp.now()) == message.text):
        db.deldet(datac[0], "otp")
        bot.send_message(message.chat.id, "<B><U><I>Changing ......</I></U></B>")
        f2a(message)
    else:
        bot.send_message(message.chat.id, "<B><U><I>INVALID TOTP</I></U></B>")
        msg = bot.send_message(message.chat.id, "<B><U><I>ENTER TOTP</I></U></B>")
        bot.register_next_step_handler(msg, totpcheck)




# --------------------- PRINTING FAV COINS ------------------------


@bot.message_handler(commands=['mydata'])
def favcheck(message):
    inshis(message, "/mydata")
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    if(datau == 0):
        bot.send_message(
            message.chat.id, "<B><U><I>You are not logged IN</I></U></B> /login to login or /signup to signup")
        return
    datac = db.lpcheck("status", message.chat.id, "chatid", "login")
    if(datac[0] == 'F'):
        db.deldet(message.chat.id, "login")
        bot.send_message(message.chat.id, "<B><U><I>You are not logged IN</I></U></B> /login to login or /signup to signup")
        return
    dataf = db.lpcheck("favcoins, weather, words", datau[0], "uname", "service")
    print(dataf)
    fav = dataf[0]
    coins = fav.split()
    x = datetime.datetime.now()
    dt = f"{x.strftime('%a  -  %b %d %Y  -  %I:%M:%S %P')}"
    bot.send_message(message.chat.id, dt)
    for i in coins:
        if(i[0].lower() == 'p'):
            pair = i[1:]
            try:
                price = client.get_symbol_ticker(symbol=pair.upper())
                pstr = price['symbol'] + ' - ' + price['price']
                bot.send_message(message.chat.id, pstr)
            except Exception as e:
                pass
            time.sleep(.01)
        else:
            pair = ''
            lstr = list()
            pstr = f"Price of <b>{i}</b>\n\n"
            for j in pair_lis:
                pair = i+j
                try:
                    price = client.get_symbol_ticker(symbol=pair.upper())
                    lstr.append(
                        f"{price['symbol']} - <b><i>{price['price']}</i></b>")
                except Exception as e:
                    pass
                time.sleep(.01)
            pstr += (',\n').join(lstr)
            bot.send_message(message.chat.id, pstr)
    if(not(dataf[1] == 'disabled')):
        url =  f"https://api.openweathermap.org/data/2.5/weather?zip={dataf[1]},in&appid={apikey.owkey}&units=imperial"
        res = requests.get(url)
        data = res.json()
        frm = f'Weather at <b><i><u>{data["name"]}</u></i></b>\n\n\
Temperature     - {data["main"]["temp"]}{deg}F\n\
Temperature Min - {data["main"]["temp_min"]}{deg}F\n\
Temperature Max - {data["main"]["temp_max"]}{deg}F\n\
Pressure        - {data["main"]["pressure"]}\n\
Humidity        - {data["main"]["humidity"]}\n\n\
<code>{data["weather"][0]["description"]}</code>'
        bot.send_message(message.chat.id, frm)
    if(not(dataf[2]) == 'disabled'):
        res = requests.get('https://random-words-api.vercel.app/word')
        data = res.json()
        frm = f'\
words         - {data[0]["word"]}\n\
definintion   - {data[0]["definition"]}\n\
pronunciation - {data[0]["pronunciation"]}'
        bot.send_message(message.chat.id, frm)

# ------------------------------- Updating favrouti coins --------------------------
@bot.message_handler(commands=['update'])
def favup(message):
    inshis(message, "/update")
    if(not message.content_type == 'text'):
        bot.send_message(message.chat.id, "<B><U><I>INVALID CREDENTIALS </I></U></B>")
        return
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    if(datau == 0):
        bot.send_message(
            message.chat.id, "<B><U><I>You are not logged IN</I></U></B> /login to login or /signup to signup")
        return
    datac = db.lpcheck("status", message.chat.id, "chatid", "login")
    if(datac[0] == 'F'):
        db.deldet(message.chat.id, "login")
        bot.send_message(message.chat.id, "<B><U><I>You are not logged IN</I></U></B> /login to login or /signup to signup")
        return
    datat = db.lpcheck("auth", datau[0], "uname", "cuser")
    if(not(datat[0] == 'OTP') and not(datat[0] == 'TOTP')):
        bot.send_message(message.chat.id, "<B><U><I>Enable</I></U></B> 2FA /2fa")
        return 
    datac = db.lpcheck("chatid", datau[0], "uname", "cuser")
    if(datat[0] == 'OTP'):
        otp = random.randint(1000, 9999)
        db.insdata(datac[0], "cotp", otp, "otp")
        bot.send_message(datac[0], f"otp for changin coin list {otp}")
        msg = bot.send_message(message.chat.id, "OTP sent successful")
        msg = bot.send_message(message.chat.id, "Enter OTP")
        bot.register_next_step_handler(msg, fcotp)
    else:
        msg = bot.send_message(message.chat.id, "Enter TOTP")
        bot.register_next_step_handler(msg, ftotp)

def fcotp(message):
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    dataotp = db.lpcheck("cotp", datau[0], "uname", "otp")
    if(str(dataotp[0]) == message.text):
        msg = bot.send_message(message.chat.id, "1.Update coin list\n2.Add or Update weather data\n3.Add Random words to subs")
        bot.register_next_step_handler(msg, serupdate)
    else:
        msg = bot.send_message(message.chat.id, "Enter OTP")
        bot.register_next_step_handler(msg, fcotp)

def ftotp(message):
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    dataotp = db.lpcheck("totp", datau[0], "uname", "otp")
    totp = pyotp.TOTP(dataotp[0])
    if(str(totp.now()) == message.text):
        msg = bot.send_message(message.chat.id, "1.Update coin list\n2.Add or Update weather data\n3.Add Random words to subs")
        bot.register_next_step_handler(msg, serupdate)
    else:
        bot.send_message(message.chat.id, "<B><U><I>INVALID TOTP</I></U></B>")
        msg = bot.send_message(message.chat.id, "<B><U><I>ENTER TOTP</I></U></B>")
        bot.register_next_step_handler(msg, ftotp)

def serupdate(message):
    if(not message.content_type == 'text'):
        bot.send_message(message.chat.id, "<B><U><I>INVALID CREDENTIALS </I></U></B>")
        return
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    if(message.text == '1'):
        dataf = db.lpcheck("favcoins", datau[0], "uname", "service")
        fav = dataf[0]
        msg = bot.send_message(message.chat.id, f"Your old list contais\n<code>{fav}</code>\n\n\
Enter Your Favorite Coins\n\n\
For Pair coins  start with p - (pbtcusdt)\n\n\
Space separated or newline eg - (dodo coti preefusdt)")
        bot.register_next_step_handler(msg, fupdate)
    elif(message.text == '2'):
        msg = bot.send_message(message.chat.id,"Enter your Pincode")
        bot.register_next_step_handler(msg, clupdate)
    elif(message.text == '3'):
        datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
        datac = db.lpcheck("chatid", datau[0], "uname", "service")
        db.insdata(datac[0], "words", "Y", "service")
        bot.send_message(message.chat.id, "<b><i>Update Successful /mydata to get the price</i></b>")
    else:
        msg = bot.send_message(message.chat.id,"Invalid Options")


def fupdate(message):
    if(not message.content_type == 'text'):
        bot.send_message(
            message.chat.id, "<B><U><I>INVALID CREDENTIALS </I></U></B>")
        db.deldet(message.chat.id, "cuser")
        return
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    datac = db.lpcheck("chatid", datau[0], "uname", "service")
    db.insdata(datac[0], "favcoins", message.text, "service")
    bot.send_message(message.chat.id, "<b><i>Update Successful /mydata to get the price</i></b>")

def clupdate(message):
    if(not message.content_type == 'text'):
        bot.send_message(
            message.chat.id, "<B><U><I>INVALID CREDENTIALS </I></U></B>")
        db.deldet(message.chat.id, "cuser")
        return
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    datac = db.lpcheck("chatid", datau[0], "uname", "service")
    db.insdata(datac[0], "weather", message.text, "service")
    bot.send_message(message.chat.id, "<b><i>Update Successful /mydata to get the price</i></b>")

#--------------------History------------------
@bot.message_handler(commands=['history', 'clrhis'])
def printhis(message):
    datau = db.lpcheck("uname", message.chat.id, "chatid", "login")
    if(datau == 0):
        bot.send_message(
            message.chat.id, "<B><U><I>You are not logged IN</I></U></B> /login to login or /signup to signup")
        return
    if(message.text == '/history'):
        his = db.hisret(datau[0])
        bot.send_message(message.chat.id, f"<b>Commands used by</b> <code>{datau[0]}</code>\n{his}")
    else:
        db.hisdel(datau[0])
        bot.send_message(message.chat.id, f"<b>History of</b> <code>{datau[0]}</code> Cleared\n/history to see history")
#--------------------Price printing-----------

@bot.message_handler(commands=['price'])
def printPrice(message):
    inshis(message, "/price")
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    itembtna = types.KeyboardButton('BTCUSDT')
    itembtnv = types.KeyboardButton('BNBUSDT')
    itembtnc = types.KeyboardButton('ETHUSDT')
    itembtnd = types.KeyboardButton('COTIUSDT')
    itembtne = types.KeyboardButton('DODOUSDT')
    markup.row(itembtna, itembtnv)
    markup.row(itembtnc, itembtnd, itembtne)
    msg = bot.send_message(
        message.chat.id, 'Enter the crypto in pairs <b>{BTCUSDT}</b>', reply_markup=markup)
    bot.register_next_step_handler(msg, processPrint)


def processPrint(message):
    try:
        price = client.get_symbol_ticker(symbol=message.text)
        print(price)
        pstr = price['symbol'] + ' - ' + price['price']
        bot.send_message(message.chat.id, pstr)
    except:
        pass


# def listener(messages):
#     for mes in messages:
#         txt = mes.text
#         if(mes.content_type == 'text' and (txt not in command_lis)):
#             if(txt[0] == 'p' or txt[0] == 'P'):
#                 pair = txt[1:]
#                 try:
#                     price = client.get_symbol_ticker(symbol=pair.upper())
#                     pstr = price['symbol'] + ' - ' + price['price']
#                     bot.send_message(mes.chat.id, pstr)
#                 except Exception as e:
#                     print(e)
#             else:
#                 pair = ''
#                 lstr = list()
#                 pstr = f"Price of <b>{txt}</b>\n\n"
#                 for i in pair_lis:
#                     pair = txt+i
#                     try:
#                         price = client.get_symbol_ticker(symbol=pair.upper())
#                         lstr.append(
#                             f"{price['symbol']} - <b><i>{price['price']}</i></b>")
#                     except Exception as e:
#                         print(e)
#                 pstr += (',\n').join(lstr)
#                 bot.send_message(mes.chat.id, pstr)


# bot.set_update_listener(listener)

bot.polling()

# # Use none_stop flag let polling will not stop when get new message occur error.
# bot.polling(none_stop=True)
# # Interval setup. Sleep 3 secs between request new message.
# bot.polling(interval=3)

# while True:  # Don't let the main Thread end.
#     pass
