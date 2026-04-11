from maxapi.context import State, StatesGroup


# Здесь все состояния бота для MAX
class MaxStates(StatesGroup):
    get_class = State()
    main_menu = State()
    gpt = State()
    get_victor_topic = State()
    get_victor_answer = State()
    settings = State()
    kontrol = State()
    get_kontrol_answer = State()
