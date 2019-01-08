import config
import telebot
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
import requests
import json
import multiprocessing

bot = telebot.TeleBot(config.TOKEN)
air_list = []
airs_dic = {}


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # message.chat.id 类型为 int，聊天 ID，如果是和机器人私聊，那么这个 ID 也就是用户的 user_id；如果是群组的话，那么就是群组的 id
    # send_message用于给用户发送消息，必须要有至少两个参数，一个是chat_id，一个是 text；
    text = "您好！我是Kencin的机器人，\n" \
           "您可以使用的命令有：\n" \
           "1. /t：获取温度和湿度\n" \
           "2. /onlight：打开LED灯\n" \
           "3. /offlight：关闭LED灯\n" \
           "4. /tkphoto：使用树莓派摄像头拍一张照片\n" \
           "5. /ticket：开始监控最低机票价格(出发城市 到达城市 日期)\n" \
           "6. /ticket2：开始监控指定航班机票价格(出发城市 到达城市 日期 航班)\n" \
           "7. /price：获取当前机票最低价格(出发城市 到达城市 日期)\n" \
           # "8. /mtlist：获取当前机票监控队列\n"
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


@bot.message_handler(commands=['ticket'])
def send_t(message):
    a = message.text.split(' ')[1:4]
    # key = str(a[0]) + " " + str(a[1]) + " " + str(a[2])
    if len(a) < 3:
        bot.reply_to(message, "输入格式有误！ 请参照 ""北京 上海 2019-01-10""")
        return
    else:
        # db = toDatabase.Monitor(a[0], a[1], a[2])
        # if db.check_exits():
        #     bot.reply_to(message, "当前输入已在监控队列中，请勿重复输入！")
        #     return
        a = json.dumps(a, ensure_ascii=False)
    try:
        publish.single("monitorticket", payload=a, hostname=config.HOST,
                       auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD})
        bot.reply_to(message, "正在尝试开始监控，请稍等~")

        # msg = subscribe.simple("monitorLowestPrice", hostname=config.HOST,
        #                         auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD})
        # data = str(msg.payload, encoding="utf-8")
        # if data == 'error':
        #     bot.reply_to(message, "出错啦！请检查输入数据的格式或者稍后再查询~")
        # if int(data) != the_price:
        #     bot.reply_to(message, "价格变动啦！原价：" + str(the_price) + "元 现价：" + str(data) + "元")
        #     the_price = data
    except Exception as e:
        print(e)


@bot.message_handler(commands=['ticket2'])
def send_t(message):
    a = message.text.split(' ')[1:5]
    # key = str(a[0]) + " " + str(a[1]) + " " + str(a[2])
    if len(a) < 4:
        bot.reply_to(message, "输入格式有误！ 请参照 ""北京 上海 2019-01-10 某某航班xxx""")
        return
    else:
        a = json.dumps(a, ensure_ascii=False)
    try:
        publish.single("monitorticket2", payload=a, hostname=config.HOST,
                       auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD})
        bot.reply_to(message, "正在尝试开始监控，请稍等~")
    except Exception as e:
        print(e)


@bot.message_handler(commands=['price'])
def send_t(message):
    a = message.text.split(' ')[1:4]
    if len(a) < 3:
        bot.reply_to(message, "输入格式有误！ 请参照 ""北京 上海 2019-01-10""")
        return
    else:
        a = json.dumps(a, ensure_ascii=False)
    try:
        publish.single("lowestprice", payload=a, hostname=config.HOST,
                       auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD}, qos=1)
        p = multiprocessing.Process(target=get_price, args= (message,) )
        p.start()
        p.join(timeout=60)
        p.terminate()
    except Exception as e:
        print(e)
        return


def get_price(message):
    msg = subscribe.simple("theLowestPrice", hostname=config.HOST,
                           auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD}, qos=1)
    data = str(msg.payload, encoding="utf-8")
    if data == 'error':
        bot.reply_to(message, "出错啦！请检查输入数据的格式或者稍后再查询~")
    dic_data = eval(data)
    bot.reply_to(message, '当前最低票价的航班是：%s， \n'
                          '来自: %s， \n'
                          '出发时间：%s， \n'
                          '到达时间：%s， \n'
                          '票价：%s' % (dic_data['flight'], dic_data['from'],
                                     dic_data['depTime'], dic_data['arrTime'], dic_data['price']))


def work():
    global airs_dic
    global air_list
    while True:
        msg = subscribe.simple("monitorLowestPrice", hostname=config.HOST,
                               auth={'username': config.MQTT_USERNAME, 'password': config.MQTT_PASSWORD}, qos=1)
        data = str(msg.payload, encoding="utf-8")
        if data == 'error':
            bot.send_message(config.MESSAGE_ID, "Ops，某一次监控失败，请等待下一次哦~")
        elif data == 'exits':
            bot.send_message(config.MESSAGE_ID, "Ops，这个监控已存在！~")
        elif data == 'ok':
            bot.send_message(config.MESSAGE_ID, "成功开启监控！~")
        else:
            dic_data = eval(data)
            bot.send_message(config.MESSAGE_ID, "从 %s 到 %s 的 航班 %s 价格有变动！ \n"
                                                "原价 %d元, 现价 %s元, \n"
                                                "来自 %s, \n"
                                                "出发时间是：%s, \n"
                                                "到达时间是：%s"
                                    % (dic_data['from_city'], dic_data['to_city'], dic_data['flight'],
                                        dic_data['beforePrice'], dic_data['price'], dic_data['from'],
                                        dic_data['depTime'], dic_data['arrTime']))


@bot.message_handler(commands=['mtlist'])
def send_t(message):
    pass
    # global price_list
    # print(price_list)
    # bot.send_message(message.chat.id, price_list[0])

# @bot.message_handler(func=lambda m:True)
# def echo_all(message):
#     bot.reply_to(message, "")


if __name__ == '__main__':
    p = multiprocessing.Process(target=work, args=())
    p.start()
    bot.polling()