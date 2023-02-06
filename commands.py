from aiogram import types, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from create_bot import bot, redis
import database as db
import keyboards as kb


english_levels = ((-1, ['time to check', 'AgACAgIAAxkBAAIDOGPbkTSYT3SrjKWcvWbs_xPGVVZEAAJtzDEbMebgShN8LdA6SPhXAQADAgADcwADLgQ']),
                  (0, ['Starter level', 'AgACAgIAAxkBAAIDOmPbkTtJ2a_aAXZWSmFEcu87HkzTAAJuzDEbMebgSvSFZ79asVQ0AQADAgADcwADLgQ']),
                  (15, ['Elementary Unit 1', 'AgACAgIAAxkBAAIDPGPbkYwPKHBOdL5Is6Y3s7FWBv5oAAJvzDEbMebgSg-gEesqiYhTAQADAgADcwADLgQ']),
                  (30, ['Elementary Unit 7', 'AgACAgIAAxkBAAIDPWPbkYznt-gVq0a6eHInL2IDupsEAAJwzDEbMebgSqXSxJSxBZnMAQADAgADcwADLgQ']),
                  (50, ['Pre-intermediate Unit 1', 'AgACAgIAAxkBAAIDQmPbkY0QrXxukLhAUK6c5ZEMk9J-AAJyzDEbMebgSk2WWgO-oIGpAQADAgADcwADLgQ']),
                  (75, ['Pre-intermediate Unit 7', 'AgACAgIAAxkBAAIDP2PbkY2Naro5tSz-NzTziYgm6PncAAJxzDEbMebgSmyCLLxoYhGMAQADAgADcwADLgQ']),
                  (100, ['Intermediate Unit 1', 'AgACAgIAAxkBAAIDRmPbkY0boN8KZ0_DltifTwYJWIQEAAJ0zDEbMebgSko5ucF0NeKYAQADAgADcwADLgQ']),
                  (125, ['Intermediate Unit 6', 'AgACAgIAAxkBAAIDRmPbkY0boN8KZ0_DltifTwYJWIQEAAJ0zDEbMebgSko5ucF0NeKYAQADAgADcwADLgQ']),
                  (150, ['Upper Intermediate Unit 1', 'AgACAgIAAxkBAAIDSmPbkY5k6XxFhp1zLUdbUoJwQ0OBAAJ2zDEbMebgSohuogMkfHDaAQADAgADcwADLgQ']),
                  (170, ['Upper Intermediate Unit 6', 'AgACAgIAAxkBAAIDSGPbkY17E83Zx7Czk0RLvYCFB87RAAJ1zDEbMebgShRBir35ryvZAQADAgADcwADLgQ']),
                  (185, ['Advanced level', 'AgACAgIAAxkBAAIDTGPbkY7uxWXmvvsnKkr4ImG9d6zeAAJ3zDEbMebgSpH8oZmV0PwXAQADAgADcwADLgQ']))


async def command_start_handler(update: types.Update):
    try:
        if type(update) == types.Message:
            await update.delete()
        else:
            await update.message.delete()
    finally:
        points = []
        for i in range(4):
            res = await redis.get(f"{update.from_user.id}:res{i}")
            points.append(res)
        points = [0 if i is None else int(i.decode()) for i in points]
        level = [i[1] for i in english_levels if sum(points) > i[0]][-1]
        if type(update) == types.Message:
            if level[0] == english_levels[0][1][0]:
                db.new_user(user_id=update.from_user.id, first_name=update.from_user.first_name,
                            last_name=update.from_user.last_name, username=update.from_user.username, reg_date=update.date)
            await update.answer_photo(
                photo=level[1],
                caption=f"<b>{['Good night', 'Good morning', 'Good day', 'Good afternoon'][(update.date.hour + 3) % 24 // 6]}, {update.from_user.first_name}!</b>\nHow do you rate your English level? Let's check up it!\n\n<b>Now you have {sum(points)}/200 points. It's {level[0]}!</b>\n\n@speakout_eng_bot",
                reply_markup=await kb.start_level_kb(points=points))
        else:
            await update.message.answer_photo(
                photo=level[1],
                caption=f"<b>{['Good night', 'Good morning', 'Good day', 'Good afternoon'][(update.message.date.hour + 3) % 24 // 6]}, {update.from_user.first_name}!</b>\nHow do you rate your English level? Let's check up it!\n\n<b>Now you have {sum(points)}/200 points. It's {level[0]}!</b>\n\n@speakout_eng_bot",
                reply_markup=await kb.start_level_kb(points=points))


async def command_help_handler(message: types.Message):
    try:
        await message.delete()
    finally:
        kb_help = types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text='✍️Write me', url='https://t.me/id7489')],
                             [types.InlineKeyboardButton(text='Hide message', callback_data='hide')]])
        msg = '''The Speakout Placement Test is designed as a diagnostic tool for use at the beginning of a course. It will help the teacher to place students at the correct level in groups of similar ability and/or to decide what pace and approach to adopt. The test has a multiple-choice format of 200 questions and covers the grammatical structures and vocabulary in the six levels of Speakout.'''
        await bot.send_photo(chat_id=message.from_user.id,
                             photo='AgACAgIAAxkBAAIBYWPYDtfPgwcdtUAtGDkhe_2rsPXTAALKxjEbBBnBShAGHQtmqyabAQADAgADcwADLQQ',
                             caption=msg + "\n\n<b>Are there any problems? Write, don't be shy.</b>",
                             reply_markup=kb_help)


async def set_commands_handler(message: types.Message):
    await message.delete()
    await bot.set_my_commands(commands=[types.BotCommand(command="start", description="Restart bot"),
                                        types.BotCommand(command="clear", description="Delete all your answers"),
                                        types.BotCommand(command="help", description="If you have some problems")])
    await bot.send_message(message.from_user.id, '<b>The command list has been successfully updated.</b>',
                           reply_markup=await kb.kb_finish(great=True, level=0))


class FSMAdd(StatesGroup):
    send_smth = State()


async def command_add_handler(message: types.Message, state: FSMContext):
    await message.delete()
    await bot.send_message(message.from_user.id, "<b>Send me photo or audio and I'll tell you it's id.</b>",
                           reply_markup=kb.kb_cancelfsm)
    await state.set_state(FSMAdd.send_smth)


async def command_clear_handler(update: types.Update):
    try:
        if type(update) == types.CallbackQuery:
            await update.message.delete()
        else:
            await update.delete()
    finally:
        if type(update) == types.CallbackQuery:
            for unit in range(4):
                await redis.delete(f"{update.from_user.id}:{unit}")
                await redis.delete(f"{update.from_user.id}:m{unit}")
                await redis.delete(f"{update.from_user.id}:res{unit}")
            await bot.send_message(update.from_user.id, "<b>Your answers were deleted.</b>",
                                   reply_markup=await kb.kb_finish(great=True, level=0, number_wrong=0))
        else:
            await bot.send_message(update.from_user.id, "<b>Are you sure?</b>\nThis action can't be undone.",
                                   reply_markup=kb.kb_sure_clear)


async def show_id(message: types.Message):
    if message.photo:
        await message.reply(f"<b>Photo ID is <code>{message.photo[0].file_id}</code></b>",
                               reply_markup=kb.kb_cancelfsm)
    elif message.audio:
        await bot.send_message(message.from_user.id, f"<b>Audio ID is <code>{message.audio.file_id}</code></b>",
                               reply_markup=kb.kb_cancelfsm)
    elif message.document:
        await bot.send_message(message.from_user.id, f"<b>Document ID is <code>{message.document.file_id}</code></b>",
                               reply_markup=kb.kb_cancelfsm)
    else:
        await bot.send_message(message.from_user.id,
                               f"<b>Your message doesn't contain photo, audio or document. Try again or cancel.</b>",
                               reply_markup=await kb.kb_finish(great=True, level=0, number_wrong=0))


async def cancel_fsm(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await bot.send_message(chat_id=call.from_user.id,
                           text='<b>Press the button below to go to the start menu.</b>',
                           reply_markup=await kb.kb_finish(great=True, level=0, number_wrong=0))
    await call.answer()


async def hide_message(update: types.Update):
    try:
        await update.message.delete()
    except Exception as e:
        print(e)
        await update.answer(
            "The bot can't hide the message because it's over 48 hours old, but you can delete it yourself.",
            reply_markup=await kb.kb_finish(great=True, level=0, number_wrong=0))


async def other_messages(message: types.Message):
    try:
        await message.delete()
    finally:
        pass


def register(dp: Dispatcher):
    dp.message.register(command_start_handler, Command(commands=["start"]))
    dp.callback_query.register(command_start_handler, lambda call: call.data == 'start')
    dp.message.register(command_help_handler, Command(commands=["help"]))
    dp.message.register(command_add_handler, Command(commands=["add"]))
    dp.message.register(set_commands_handler, Command(commands=["set_commands"]))
    dp.message.register(command_clear_handler, Command(commands=["clear"]))
    dp.callback_query.register(command_clear_handler, lambda call: call.data == 'clear')
    dp.message.register(show_id, FSMAdd.send_smth)
    dp.callback_query.register(hide_message, lambda call: call.data == 'hide')
    dp.callback_query.register(cancel_fsm, lambda call: call.data == 'cancelFSM')
    dp.message.register(other_messages)
