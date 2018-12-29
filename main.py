import config
import telebot
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
import requests


bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # message.chat.id 类型为 int，聊天 ID，如果是和机器人私聊，那么这个 ID 也就是用户的 user_id；如果是群组的话，那么就是群组的 id
    # send_message用于给用户发送消息，必须要有至少两个参数，一个是chat_id，一个是 text；
    text = "你好！我是Kencin的机器人，\n" \
           "您可以使用的命令有：\n" \
           "1. /t：获取温度和湿度\n" \
           "2. /onlight：打开LED灯\n" \
           "3. /offlight：关闭LED灯\n" \
           "4. /tkphoto：拍一张照片"
    bot.send_message(message.chat.id, text)
    print(message.chat.id)


@bot.message_handler(commands=['t'])
def send_t(message):
    bot.send_message(message.chat.id, '获取温度和湿度')
    publish.single("raspberry", payload="getT", hostname=config.HOST,
                   auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD})
    msg = subscribe.simple("T_H", hostname=config.HOST,
                   auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD})
    data = str(msg.payload, encoding="utf-8")
    dic_data = eval(data)
    bot.send_message(message.chat.id, '当前宿舍温度为：%.1f ° 湿度为: %d%%' % (dic_data['T'], dic_data['H']))


@bot.message_handler(commands=['onlight'])
def send_t(message):
    bot.send_message(message.chat.id, '打开LED小灯')
    publish.single("raspberry", payload="TurnOnLed", hostname=config.HOST,
                   auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD})


@bot.message_handler(commands=['offlight'])
def send_t(message):
    bot.send_message(message.chat.id, '关闭LED小灯')
    publish.single("raspberry", payload="TurnOffLed", hostname=config.HOST,
                   auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD})


@bot.message_handler(commands=['tkphoto'])
def send_t(message):
    # photo = open('C:/Users/Administrator/Pictures/world.jpg', 'rb')
    # bot.send_photo(message.chat.id, photo)
    bot.send_message(message.chat.id, '拍照')
    publish.single("raspberry", payload="tkphoto", hostname=config.HOST,
                   auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD})
    msg = subscribe.simple("photo", hostname=config.HOST,
                           auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD})
    data = str(msg.payload, encoding="utf-8")
    with open("tmp.jpg", "wb") as codes:
        codes.write(requests.get(data).content)
    bot.send_message(message.chat.id, data)
    photo = open('tmp.jpg', 'rb')
    bot.send_photo(message.chat.id, photo)


# @bot.message_handler(func=lambda m:True)
# def echo_all(message):
#     bot.reply_to(message, "")


if __name__ == '__main__':
    bot.polling()
