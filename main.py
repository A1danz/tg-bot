from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import ParseMode
from telegram import Update, Bot
from config import TOKEN, VK_TOKEN, HEADERS, quality
import requests
import validators
import time
import vk_api
from bs4 import BeautifulSoup
import tiktok_downloader
from selenium_main import down_vk
import pytube


def start(update, context):
    global is_chosen
    # запись в БД started = 1
    update.message.reply_text("📍 Привет, это SaveBot!\n📍 Я умею сохранять видео, фото с YouTube, TikTok, VK.",
                              reply_markup=markup)
    is_chosen = "start"
    updater.dispatcher.add_handler(chose_hand)


def chosen(update, context):
    global is_chosen
    if update.message.text.lower()[1:] == "tiktok":
        is_chosen = "TikTok"
    elif update.message.text.lower()[1:] == "youtube":
        is_chosen = "Youtube"
    elif update.message.text.lower()[1:] == "vk":
        is_chosen = "Vk"
    elif update.message.text[1:].lower() == "вернуться к выбору":
        update.message.reply_text(f"⬅️Возвращение к выбору...",
                                  reply_markup=markup)
    if update.message.text.lower()[1:] not in ["tiktok", "youtube", "vk"] and update.message.text[1:].lower() == "вернуться к выбору":
        update.message.reply_text(f"❌ Неопознанная команда")
    else:
        update.message.reply_text(f"✅ {is_chosen[0].upper() + is_chosen[1:]} успешно выбран\n➡Введите ссылку на видео/фото для дальнейшей работы",
                                  reply_markup=back_markup)
        updater.dispatcher.remove_handler(chose_hand)
        updater.dispatcher.add_handler(link_hand)


def down_link(update: Update, context):
    global k
    global links_to_down
    if update.message.text != "⬅Вернуться к выбору":
        update.message.reply_text("🛠Проверяю...", reply_markup=ReplyKeyboardRemove())
        time.sleep(1)
        k = 0
        link = update.message.text
        if (link.startswith("https://") or link.startswith("http://")) == 0:
            link = "https://" + link
        if not validators.url(link):
            update.message.reply_text("❌ Вы отправили не ссылку")
            update.message.reply_text("➡ Отправьте другую ссылку")
            k = 2
        try:
            if k != 2 and requests.get(link).status_code != 200:
                update.message.reply_text("❌ Недопустимая ссылка, проверьте ее правильность")
                update.message.reply_text("➡ Отправьте другую ссылку")
                k = 2
        except:
            update.message.reply_text("❌ Недопустимая ссылка, проверьте ее правильность")
            update.message.reply_text("➡ Отправьте другую ссылку")
            k = 2
        if "vk.com" in link and is_chosen == "Vk" and k != 2:
            if "photo" in link:
                update.message.reply_text("✅VK-ссылка успешна распознана...")
                time.sleep(0.5)
                update.message.reply_text("🔋Начинаю скачивание...")
                try:
                    path_to_photo = download_vk(link)
                    if path_to_photo:
                        k = 1
                        update.message.reply_text("Успешное скачивание")
                        bot.send_photo(chat_id=update.message.chat_id, photo=open(path_to_photo, "rb"))
                    else:
                        update.message.reply_text("Бот сломался, приносим свои извинения")
                except:
                    update.message.reply_text("Бот не смог скачать это фото, попробуйте еще раз")
            elif "video" in link:
                update.message.reply_text("✅VK-ссылка успешна распознана...")
                time.sleep(0.5)
                update.message.reply_text("🔋Начинаю скачивание...")
                try:
                    links_to_down = down_vk(link)
                    qualities = quality[:len(links_to_down)]
                    if len(qualities) == 6:
                        q_btns = [[btns[0], btns[1], btns[2]],
                                [btns[3], btns[4], btns[5]]]
                    if len(qualities) == 5:
                        q_btns = [[btns[0], btns[1], btns[2]],
                                [btns[3], btns[4]]]
                    elif len(qualities) == 4:
                        q_btns = [[btns[0], btns[1]],
                                 [btns[2], btns[3]]]
                    elif len(qualities) == 3:
                        q_btns = [[btns[0], btns[1]],
                                 [btns[2]]]
                    inl_keyboard = InlineKeyboardMarkup(q_btns)
                    update.message.reply_text(text="Пожалуйста, выберите качество:", reply_markup=inl_keyboard)
                except Exception as e:
                    print(e)
                    update.message.reply_text("Попытка не удалась, попробуйте еще раз")
            else:
                update.message.reply_text("☹ Вы отправили некорректную ссылку, проверьте ее еще раз")
        elif "tiktok.com" in link and is_chosen == "TikTok" and k != 2:
            if "video" in link:
                update.message.reply_text("✅TikTok-видео успешно распознано...")
                time.sleep(0.5)
                update.message.reply_text("🔋Начинаю скачивание...")
                try:
                    path_to_down = download_tiktok(link)
                    k = 1
                    bot.sendVideo(chat_id=update.message.chat_id, video=open(path_to_down, "rb"))
                except:
                    update.message.reply_text("Бот сломался, приносим свои извинения")
            else:
                update.message.reply_text("Вы отправили ссылку, в которой нет видео")
        elif "youtube.com" in link or "youtube" in link and is_chosen == "youtube" and k != 2:
            if 'watch' in link:
                link_youtube = link
                updater.dispatcher.remove_handler(link_hand)
                update.message.reply_text("Выберите качество, в котором вы хотите скачать видео: ", reply_markup=quality_markup)
                updater.dispatcher.add_handler(youtube_quality)
            else:
                update.message.reply_text('Вы отправили неверную ссылку, попробуйте ещё раз')
        elif k != 2:
            update.message.reply_text("☹ Вы отправили некорректную ссылку, проверьте ее еще раз")
        if k == 1:
            update.message.reply_text("Выберите дальнейшие действия:", reply_markup=mes_markup)
            updater.dispatcher.add_handler(btn_handler)
    else:
        updater.dispatcher.remove_handler(link_hand)
        update.message.reply_text(text="Выбирайте:", reply_markup=markup)
        updater.dispatcher.add_handler(chose_hand)


def video_youtube(link, quality):
    yt = pytube.YouTube(link)
    videos = yt.streams.filter(res=quality).first()
    path = 'videos/youtube'
    if videos.filesize < 52428800:
        videos.download(path)
        title = yt.title
        for symb in ["/", ":", "*", "?", "^", ">", "<", "|"]:
            if symb in title:
                title = title.replace(symb, "")
        result_video = path + f'/{title}.mp4'
        return result_video
    return None


def mes_keyboard_handler(update: Update, context):
    query = update.callback_query
    data = query.data

    if data == "back_btn":
        query.edit_message_text(text="Вернул 🪃",
                                parse_mode=ParseMode.MARKDOWN,
                                )
        bot.sendMessage(chat_id=query.from_user["id"], text="Выбирайте:", reply_markup=markup)
        updater.dispatcher.remove_handler(link_hand)
        updater.dispatcher.add_handler(chose_hand)
    elif data == "continue_btn":
        query.edit_message_text(text="Вставьте ссылку",
                                parse_mode=ParseMode.MARKDOWN,)
    elif "p" in data:
        ind = quality.index(data)
        link = links_to_down[len(links_to_down) - 1 - ind]
        req = requests.get(link, headers=HEADERS, stream=True)
        query.edit_message_text(text="Качество успешно выбрано",
                                parse_mode=ParseMode.MARKDOWN,
                                )
        if int(req.headers['Content-Length']) / 1024 / 1024 <= 50:
            bot.sendVideo(chat_id=query.from_user["id"], video=req.content)
        else:
            bot.sendMessage(chat_id=query.from_user["id"], text="Из-за огрничений я не могу отправить файл, который"
                                                                "весит больше 50 МБ, поэтому я отправлю ссылку, по которой"
                                                                "бдует возможно скачать видео")
            bot.sendMessage(chat_id=query.from_user["id"], text=link)


def download_youtube(update, context):
    global link_youtube
    global k
    all_quality = {'144p', '240p', '360p', '480p', '720p'}
    quality_video = update.message.text
    if quality_video not in all_quality:
        update.message.reply_text(
            'Такого качества на ютубе не существует, поэтому выберите качество из предложенного списка'
        )
        updater.dispatcher.add_handler(youtube_quality)
    else:
        update.message.reply_text(f'Качество {quality_video} выбрано')
        result_video = video_youtube(link_youtube, quality_video)
        if not result_video:
            update.message.reply_text('видео слишком большого размера')
        else:
            k = 1
            update.message.reply_text('Видео из youtube успешно скачано')
            time.sleep(0.1)
            update.message.reply_text('Придётся немного подождать, мы загружаем видео...')
            bot.sendVideo(chat_id=update.message.chat_id, video=open(result_video, "rb"))
            updater.dispatcher.remove_handler(youtube_quality)
            update.message.reply_text("Выберите дальнейшие действия:", reply_markup=mes_markup)
            updater.dispatcher.add_handler(btn_handler)


def download_vk(link):
    login, password = '89962167133', 'test_yandex'
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()

    url_input = link
    id_ph = url_input.split('%')[0]
    id_ph = id_ph.split('photo')[-1]

    owner_id, photo_id = id_ph.split('_')
    filename = owner_id + '_' + photo_id
    response = vk.photos.getById(photos=[f'{id_ph}'])
    if response[0]:
        response = response[0]['sizes']
        url = response[-1]['url']
        time.sleep(0.1)

        api = requests.get(url)

        with open(r'photos/%s' % f'{filename}.jpg', 'wb') as file:
            file.write(api.content)
        return r'photos/%s' % f'{filename}.jpg'
    else:
        return None


def download_tiktok(link):
    snaptik_obj = tiktok_downloader.snaptik(link)
    video_id = link.split("video/")[-1].split("?")[0]
    path_to_tt_video = f"videos/tiktok/{video_id}.mp4"
    snaptik_obj.get_media()[0].download(path_to_tt_video)
    return path_to_tt_video


if __name__ == "__main__":
    # input handlers
    chose_hand = MessageHandler(Filters.all, chosen)
    link_hand = MessageHandler(Filters.text, down_link)
    youtube_quality = MessageHandler(Filters.all, download_youtube)
    btn_handler = CallbackQueryHandler(callback=mes_keyboard_handler, pass_chat_data=True)
    start_hand = CommandHandler("start", start)

    # input markups
    mes_btns = [[InlineKeyboardButton("⬅Вернуться к выбору", callback_data="back_btn"),
                 InlineKeyboardButton("Продолжить скчивание➡", callback_data="continue_btn")]]
    mes_markup = InlineKeyboardMarkup(mes_btns)
    reply_keyboard = [['⚫TikTok', '🔵VK'],
                      ['🔴YouTube', ]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    back_keyboard = [["⬅Вернуться к выбору"]]
    back_markup = ReplyKeyboardMarkup(back_keyboard, one_time_keyboard=True, resize_keyboard=True)

    btns = [InlineKeyboardButton("144p", callback_data="144p"), InlineKeyboardButton("240p", callback_data="240p"),
             InlineKeyboardButton("360p", callback_data="360p"), InlineKeyboardButton("480p", callback_data="480p"),
            InlineKeyboardButton("720p", callback_data="720p"), InlineKeyboardButton("1080p", callback_data="1080p")]

    quality_keyboard = [['144p', '240p', '360p'],
                        ['480p', '720p']]
    quality_markup = ReplyKeyboardMarkup(quality_keyboard, one_time_keyboard=True, reply_keyboard=True)

    link_youtube = ''
    k = 2
    USERAGENT = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
    bot = Bot(token=TOKEN)
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(btn_handler)
    dp.add_handler(start_hand)

    updater.start_polling()
    updater.idle()