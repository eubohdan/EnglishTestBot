from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def start_level_kb(points: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=f'''{('', f'✅{points[0]}/50')[bool(points[0])]} "Starter and Elementary" level part''',
                   callback_data='check|0')
    builder.button(text=f'''{('', f'✅{points[1]}/50')[bool(points[1])]} "Pre-intermediate" level part''',
                   callback_data='check|1')
    builder.button(text=f'''{('', f'✅{points[2]}/50')[bool(points[2])]} "Intermediate" level part''',
                   callback_data='check|2')
    builder.button(text=f'''{('', f'✅{points[3]}/50')[bool(points[3])]} "Upper Intermediate and Advanced" level part''',
                   callback_data='check|3')
    builder.adjust(1)
    return builder.as_markup()


async def test_kb(question: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=question['a'][3:], callback_data=f"check|{question['level']}|{question['number']}|a")
    builder.button(text=question['b'][3:], callback_data=f"check|{question['level']}|{question['number']}|b")
    builder.button(text=question['c'][3:], callback_data=f"check|{question['level']}|{question['number']}|c")
    builder.button(text=question['d'][3:], callback_data=f"check|{question['level']}|{question['number']}|d")
    builder.button(text="Exit", callback_data='finish_sure')
    if any([len(i) > 18 for i in [question['a'], question['b'], question['c'], question['d']]]):
        builder.adjust(1)
    else:
        builder.adjust(2, 2, 1)
    return builder.as_markup()


kb_cancelfsm = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Thank you, exit', callback_data='cancelFSM')]])


async def kb_finish(great: bool, level: int, number_wrong: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if not great:
        builder.button(text="To see mistakes", callback_data=f"mistakes|{level}|0|{number_wrong}")
    builder.button(text='Back to main', callback_data='start')
    builder.adjust(1)
    return builder.as_markup()


async def kb_mistakes(level: str, num: str, number_wrong: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if int(num) > 0:
        builder.button(text="<-- Previous", callback_data=f"mistakes|{level}|{int(num) - 1}|{number_wrong}")
    builder.button(text='Back to main', callback_data='finish_sure')
    if int(num) + 1 < int(number_wrong):
        builder.button(text="Next -->", callback_data=f"mistakes|{level}|{int(num) + 1}|{number_wrong}")
    builder.adjust(3)
    return builder.as_markup()


kb_sure_clear = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Wipe all data', callback_data='clear')],
                     [InlineKeyboardButton(text='Back to main', callback_data='start')]])
