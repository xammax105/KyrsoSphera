from aiogram.fsm.state import StatesGroup, State


class RasStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_password = State()
    AddCourseStates = State()
    AddDescription = State()
    AddSourseState = State()
    AddCostState = State()
    AddNewCostState = State()
    AddNewCourseStates = State()
    AddNewDescription = State()
    AddNewSourseState = State()
    AddRewievState = State()
    waiting_for_instructions = State()



    waiting_for_tag_search = State()

