# -*- coding: utf-8 -*-
#!/usr/bin/python

from __future__ import division
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from emoji import emojize
import sqlite3
import datetime


TOKEN = '541426573:AAGTVtuqHGuljiHI5oeAQ75ssnZgUCVlLtU'
USER = {}
EXAM = {}


def database(sql):
    db = sqlite3.connect("aeroschool.db")
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    db.close()
    return result

def start(bot, update):
    global USER
    global EXAM

    user = update.effective_user.id
    # EXAM[user] = [QUESTIONS, WRONG_ANSWERS, INDEX, CORRECT_ANSWER, START_TIME]
    EXAM[user] = [[], [], 0, 0, 0]
    USER[user] = []
    result = database("SELECT * FROM Courses;")
    keyboard = []
    msg = "*List of Courses:*\n\n"

    for i in range(len(result)):
        msg += "\t\t" + str(result[i][0]) + ". " + result[i][1] + "\n"
        row = []
        row.append(InlineKeyboardButton(str(result[i][1]), callback_data=result[i][1]))
        keyboard.append(row)

    msg += "\nSelect a Course:"
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)



def button(bot, update):
    global USER
    global EXAM
    user = update.effective_user.id
    query = update.callback_query
    option_name = query.data
    USER[user].append(option_name)
    if option_name == "back":
        USER[user] = USER[user][:-2]
        EXAM[user] = [[], [], 0, 0, 0]

    if len(USER[user]) == 0:
        msg, reply_markup = course_button(bot, update, user)
        bot.edit_message_text(text=msg,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          parse_mode=ParseMode.MARKDOWN,
                          reply_markup=reply_markup)

    elif len(USER[user]) == 1:
        msg, reply_markup = lesson_button(bot, update, user)
        bot.edit_message_text(text=msg,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          parse_mode=ParseMode.MARKDOWN,
                          reply_markup=reply_markup)

    elif len(USER[user]) == 2:
        msg, reply_markup = topic_button(bot, update, user)
        bot.edit_message_text(text=msg,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          parse_mode=ParseMode.MARKDOWN,
                          reply_markup=reply_markup)

    elif len(USER[user]) == 3 and USER[user][2] != "Exam":
        msg, reply_markup, img = tutorial_button(bot, update, user)
        bot.edit_message_text(text=msg,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          parse_mode=ParseMode.MARKDOWN,
                          reply_markup=reply_markup)

        for i in range(len(img)):
            bot.sendPhoto(chat_id=query.message.chat_id,
                          photo = img[i].split("\n")[0],
                          caption=img[i].split("\n")[1])

    elif  USER[user][-1] == "Exam":
        exam(bot, update, user, query)

    elif(USER[user][-1] == "A"
        or USER[user][-1] == "B"
        or USER[user][-1] == "C"
        or USER[user][-1] == "D"):

        if USER[user][-1] == EXAM[user][0][EXAM[user][2]][6]:
            EXAM[user][3] += 1

        else:
            EXAM[user][0][EXAM[user][2]].append(USER[user][-1])
            EXAM[user][1].append(EXAM[user][0][EXAM[user][2]])
        USER[user] = USER[user][:-1]
        EXAM[user][2] += 1

        if EXAM[user][2]== len(EXAM[user][0]):
            keyboard = []
            if EXAM[user][3] != len(EXAM[user][0]):
                keyboard.append([InlineKeyboardButton("Review Exam", callback_data="review")])
            keyboard.append([InlineKeyboardButton(emojize(":arrow_backward:", use_aliases=True), callback_data="back")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            exam_duration = datetime.datetime.now().replace(microsecond=0) - EXAM[user][4]

            
            msg = emojize(":warning:", use_aliases=True) + " Exam Statistics\n\n\n"
            msg += emojize(":pencil2:", use_aliases=True) + " Total Questions: %s\n\n" % len(EXAM[user][0])
            msg += emojize(":white_check_mark:", use_aliases=True) + " Correct Answers: %s\n\n" % EXAM[user][3]
            msg += emojize(":alarm_clock:", use_aliases=True) + " Exam Duration: %s\n\n" % exam_duration

            
            
            msg += emojize(":100:", use_aliases=True) + "Exam Score: %s" % (float("%.4f" % (EXAM[user][3] / len(EXAM[user][0]))) * 100) + "%"

            EXAM[user][2] = 0
            EXAM[user][3] = 0
            EXAM[user][0] = []
            EXAM[user][4] = 0
            bot.edit_message_text(text=msg,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          parse_mode=ParseMode.MARKDOWN,
                          reply_markup=reply_markup)
        else:
            ask_question(bot, update, user, query)

    elif USER[user][3] == "review" or USER[user][3] == "next":
        msg, reply_markup = review(bot, update, user, query)
        bot.edit_message_text(text=msg,
                      chat_id=query.message.chat_id,
                      message_id=query.message.message_id,
                      parse_mode=ParseMode.MARKDOWN,
                      reply_markup=reply_markup)

def review(bot, update, user, query):
    global USER
    global EXAM
    keyboard = []

    msg = "%s\n%s\n%s\n%s\n%s\n\n" %(EXAM[user][1][EXAM[user][2]][0],
                                  EXAM[user][1][EXAM[user][2]][2],
                                  EXAM[user][1][EXAM[user][2]][3],
                                  EXAM[user][1][EXAM[user][2]][4],
                                  EXAM[user][1][EXAM[user][2]][5])

    msg += emojize(":x:", use_aliases=True) + " Your answer was  *%s*\n" % EXAM[user][1][EXAM[user][2]][7]
    msg += emojize(":white_check_mark:", use_aliases=True) + " Correct answer is *%s*" % EXAM[user][1][EXAM[user][2]][6]
    EXAM[user][2] += 1
    USER[user] = USER[user][:-1]
    if EXAM[user][2] == len(EXAM[user][1]):
        EXAM[user][2]= 0
        EXAM[user][1] = []
    else:
        keyboard.append([InlineKeyboardButton("Next", callback_data="next")])
    keyboard.append([InlineKeyboardButton(emojize(":arrow_backward:", use_aliases=True), callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return msg, reply_markup

def exam(bot, update, user, query):
    global USER
    global EXAM

    result = database("SELECT * FROM '%s' WHERE lesson='%s' AND topic='%s';" % (USER[user][0], USER[user][1], USER[user][2]))
    keyboard = []
    msg = """%s *selected course:* _%s_
%s *selected lesson:* _%s_
%s *selected topic:*   _%s_\n\n""" % (emojize(":books:", use_aliases=True),
                                        USER[user][0],
                                        emojize(":closed_book:", use_aliases=True),
                                        USER[user][1],
                                        emojize(":book:", use_aliases=True),
                                        USER[user][2])


    question_list = result[0][4].split("\r\n\r\n\r\n")
    for question in question_list:
        answer = question.split("\n")[-1]
        d = question.split("\n")[-2]
        c = question.split("\n")[-3]
        b = question.split("\n")[-4]
        a = question.split("\n")[-5]
        text = question.split("-----")[0]

        if len(question.split("-----")) == 3: #This means that the question has image
            img = question.split("-----")[1]
        else:
            img = None

        EXAM[user][0].append([text, img, a, b, c, d, answer])

    EXAM[user][4] = datetime.datetime.now().replace(microsecond=0)
    ask_question(bot, update, user, query)

def ask_question(bot, update, user, query):
        global USER
        global EXAM

        result = database("SELECT * FROM '%s' WHERE lesson='%s' AND topic='%s';" % (USER[user][0], USER[user][1], USER[user][2]))
        keyboard = []
        msg = """%s *selected course:* _%s_
%s *selected lesson:* _%s_
%s *selected topic:*   _%s_\n\n""" % (emojize(":books:", use_aliases=True),
                                        USER[user][0],
                                        emojize(":closed_book:", use_aliases=True),
                                        USER[user][1],
                                        emojize(":book:", use_aliases=True),
                                        USER[user][2])

        msg += emojize(":information_source:", use_aliases=True) + " _Question %s of %s_\n\n" % (EXAM[user][2] + 1, len(EXAM[user][0]))

        keyboard.append([InlineKeyboardButton("A", callback_data="A"),
                         InlineKeyboardButton("B", callback_data="B"),
                         InlineKeyboardButton("C", callback_data="C"),
                         InlineKeyboardButton("D", callback_data="D")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        msg += "%s\n%s\n%s\n%s\n%s" %(EXAM[user][0][EXAM[user][2]][0],
                                      EXAM[user][0][EXAM[user][2]][2],
                                      EXAM[user][0][EXAM[user][2]][3],
                                      EXAM[user][0][EXAM[user][2]][4],
                                      EXAM[user][0][EXAM[user][2]][5])

            
        bot.edit_message_text(text=msg,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          parse_mode=ParseMode.MARKDOWN,
                          reply_markup=reply_markup)

        if EXAM[user][0][EXAM[user][2]][1] != None:
            bot.sendPhoto(chat_id=query.message.chat_id,
                          photo = EXAM[user][0][EXAM[user][2]][1].replace("\r\n", ""))

#QUESTIONS[INDEX]
def tutorial_button(bot, update, user):
    result = database("SELECT * FROM '%s' WHERE lesson='%s' AND topic='%s';" % (USER[user][0], USER[user][1], USER[user][2]))
    keyboard = []
    msg = """%s *selected course:* _%s_
%s *selected lesson:* _%s_
%s *selected topic:*   _%s_\n\n""" % (emojize(":books:", use_aliases=True),
                                        USER[user][0],
                                        emojize(":closed_book:", use_aliases=True),
                                        USER[user][1],
                                        emojize(":book:", use_aliases=True),
                                        USER[user][2])

    msg += result[0][4]
    if result[0][-1]:
        img = result[0][-1]
        img = img.split("\r\n\r\n")
    else:
        img = None

    keyboard.append([InlineKeyboardButton(emojize(":arrow_backward:", use_aliases=True), callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return msg, reply_markup, img


def topic_button(bot, update, user):
    result = database("SELECT * FROM '%s' WHERE lesson='%s';" % (USER[user][0], USER[user][1]))

    keyboard = []
    msg = """%s *selected course:* _%s_
%s *selected lesson:* _%s_
\nTopics:\n\n""" % (emojize(":books:", use_aliases=True),
                                    USER[user][0],
                                    emojize(":closed_book:", use_aliases=True),
                                    USER[user][1])

    for i in range(len(result)):
        msg += "\t\t" + str(result[i][2]) + ". " + str(result[i][3]) + "\n"
        row = []
        row.append(InlineKeyboardButton(str(result[i][3]), callback_data=result[i][3]))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton(emojize(":arrow_backward:", use_aliases=True), callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return msg, reply_markup

def lesson_button(bot, update, user):
    result = database("SELECT * FROM '%s';" % USER[user][0])
    keyboard = []
    msg = emojize(":books:", use_aliases=True) + " *selected course:* _%s_\n\nTable of Content:\n\n" % USER[user][0]
    for i in range(len(result)):
        if str(result[i][1]) in msg:
            pass
        else:
            msg += "\t\t" + str(result[i][0]) + ". " + str(result[i][1]) + "\n"
            row = []
            row.append(InlineKeyboardButton(str(result[i][1]), callback_data=result[i][1]))
            keyboard.append(row)

    keyboard.append([InlineKeyboardButton(emojize(":arrow_backward:", use_aliases=True), callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return msg, reply_markup

def course_button(bot, update, user):
    result = database("SELECT * FROM Courses;")
    keyboard = []
    msg = "*List of Courses:*\n\n"

    for i in range(len(result)):
        msg += "\t\t" + str(result[i][0]) + ". " + result[i][1] + "\n"
        row = []
        row.append(InlineKeyboardButton(str(result[i][1]), callback_data=result[i][1]))
        keyboard.append(row)

    msg += "\nSelect a Course:"
    reply_markup = InlineKeyboardMarkup(keyboard)

    return msg, reply_markup


updater = Updater(TOKEN)
dispatcher = updater.dispatcher

updater.dispatcher.add_handler(CallbackQueryHandler(button))
dispatcher.add_handler(CommandHandler("start", start))



updater.start_polling()

updater.idle()
