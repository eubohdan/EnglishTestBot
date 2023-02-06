from aiogram import types, Dispatcher
import database as db
import keyboards as kb
from create_bot import redis


async def placement_test(call: types.CallbackQuery) -> None:
    query = call.data.split('|')
    if len(query) == 4:
        _, level, question_num, answer = call.data.split('|')  # номер и ответ ПРЕДЫДУЩЕГО ВОПРОСА
        await redis.lset(name=f"{call.from_user.id}:{level}",
                         index=int(question_num) - 1,
                         value=answer)
        try:
            await call.message.delete()
        finally:
            if int(question_num) != 50:
                result = await redis.hgetall(name=100 * int(level) + int(question_num) + 1)
                question = {}
                for k, v in result.items():
                    question[k.decode()] = v.decode()
                msg_text = f"<b>{int(question_num) + 1}.</b> {question['question']}"
                img = await redis.get(name=f"photo{int(question_num) + 1}")
                await call.message.answer_photo(photo=img.decode(), caption=msg_text,
                                                reply_markup=await kb.test_kb(question=question))
            else:
                users_answers = await redis.lrange(name=f"{call.from_user.id}:{level}", start=0, end=-1)
                correct_answers = await redis.lrange(name="answers" + level, start=0, end=-1)
                correct_counter, wrong = 0, []
                for answer_num in range(len(users_answers)):
                    if users_answers[answer_num] == correct_answers[answer_num]:
                        correct_counter += 1
                    elif users_answers[answer_num] != '-':
                        wrong.append(f"{answer_num + 1}|{users_answers[answer_num].decode()}")
                msg = f"<b>Your result is {correct_counter}/50!</b>\n\n"
                await redis.set(name=f"{call.from_user.id}:res{level}", value=correct_counter)
                await redis.delete(f"{call.from_user.id}:m{level}")
                db.set_answers(level=level, score=correct_counter, user_id=call.from_user.id, last_date=str(call.message.date))
                if wrong:
                    msg += f"<b>You have errors in the following tasks:</b> <i>{', '.join([i.split('|')[0] for i in wrong])}</i>."
                    await redis.delete(f"{call.from_user.id}:m{level}")
                    await redis.rpush(f"{call.from_user.id}:m{level}", *wrong)
                else:
                    msg += "You completed all the tasks without any errors! Great!"
                await call.message.answer_photo(photo='AgACAgIAAxkBAAIGk2PeRzl5Z7fcWpoCLAX9_0BP7RdLAAIyxjEbYazxSthfXfJXkUarAQADAgADcwADLgQ',
                                                caption=msg,
                                                reply_markup=await kb.kb_finish(great=not bool(wrong), level=level, number_wrong=len(wrong)))
    else:
        try:
            await call.message.delete_reply_markup()
        finally:
            result = await redis.hgetall(name=1 + int(query[1]) * 100)
            question = {}
            for k, v in result.items():
                question[k.decode()] = v.decode()
            if not await redis.exists(f"{call.from_user.id}:{query[1]}"):
                await redis.rpush(f"{call.from_user.id}:{query[1]}", *['-' for _ in range(50)])
            img = await redis.get(name='photo1')
            await call.message.answer_photo(photo=img.decode(),
                                            caption=f"<b>1.</b> {question['question']}",
                                            disable_notification=True,
                                            reply_markup=await kb.test_kb(question=question))
    await redis.close()


async def finish_sure(call: types.CallbackQuery) -> None:
    msg = call.message.text
    markup = call.message.reply_markup
    try:
        if "ARE YOU SURE" not in msg:
            await call.message.edit_caption(
                caption=msg + "\n\n<b>ARE YOU SURE?</b>\n <i>If you want to exit, press the button again, otherwise continue.</i>",
                reply_markup=markup)
        else:
            await call.message.delete()
            await call.message.answer(text="<b>Press the button below to go to main.</b>",
                                      reply_markup=await kb.kb_finish(great=True, level=0, number_wrong=0))
    except:
        await call.message.answer(text="<b>Press the button below to go to main.</b>",
                                  reply_markup=await kb.kb_finish(great=True, level=0, number_wrong=0))


async def mistakes(call: types.CallbackQuery) -> None:
    _, level, num, number_wrong = call.data.split('|')
    try:
        await call.message.delete()
    finally:
        result = await redis.lrange(name=f"{call.from_user.id}:m{level}", start=num,
                                    end=int(num) + 1)  # список одной ошибки
        mistake = result[0].decode().split('|')  # список, строка номер ошибки и строка буква ответа
        result = await redis.hgetall(name=int(mistake[0]) + int(level) * 100)  # словарь со всеми данными вопроса
        question = {}  # корректный словарь со всеми данными вопроса
        for k, v in result.items():
            question[k.decode()] = v.decode()
        new_sentence = question['question'].replace('__________', f"<u><i><s>{question[mistake[1]][3:]}</s> <b>{question[question['correct']][3:]}</b></i></u>")
        msg = f'''<b>{mistake[0]}.</b> {new_sentence}''' #\n\n{question['rule']} показывать вместе с ошибкой правила
        await call.message.answer(text=msg,
                                  reply_markup=await kb.kb_mistakes(level=level, num=num, number_wrong=number_wrong))
        await redis.close()


def register(dp: Dispatcher):
    dp.callback_query.register(placement_test, lambda call: call.data.startswith('check'))
    dp.callback_query.register(mistakes, lambda call: call.data.startswith('mistakes'))
    dp.callback_query.register(finish_sure, lambda call: call.data == 'finish_sure')
