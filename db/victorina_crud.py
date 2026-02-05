import aiosqlite


async def create_victorina(class_num: int, topic: str, question_list: list):
    conn = await aiosqlite.connect("lead.db")
    cursor = await conn.execute(
        "INSERT INTO victorins (class, topic) VALUES (?,?)", (class_num, topic)
    )
    await conn.commit()
    vict_id = cursor.lastrowid
    print(question_list)
    # Сделать так,чтобы в БД через цикл создавалось 4 вопроса
    for quest_dic in question_list:
        cursor = await conn.execute(
            "INSERT INTO questions (question, vict_id) VALUES (?,?)",
            (quest_dic["question"], vict_id),
        )
        await conn.commit()
        quest_id = cursor.lastrowid  # Id последнего созданного вопроса
        for answer in quest_dic["answers"]:
            correct = False
            if answer == quest_dic["correct_answer"]:
                correct = True
            cursor = await conn.execute(
                "INSERT INTO answers (text, quest_id, correct) VALUES (?,?,?)",
                (answer, quest_id, correct),
            )
            await conn.commit()

    await conn.close()


async def get_victorina(class_num: int, topic: str):
    '''Достаем викторину из БД и формируем из нее список со словарями вопросов'''
    question_list = []
    async with aiosqlite.connect("lead.db") as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM victorins WHERE topic = ? and class = ?", (topic, class_num)
        )
        victorina = await cursor.fetchone()
        if victorina:
            victorina_dic = dict(victorina)
            cursor = await db.execute(
                "SELECT * FROM questions WHERE vict_id=?", (victorina_dic["id"],)
            )
            questions = await cursor.fetchall() #[<cursor.Row>,<cursor.Row>,<cursor.Row>,<cursor.Row>]
            for question in questions:
                question_dic = dict(question)
                # Получим ответы для данного вопроса
                cursor = await db.execute(
                    "SELECT * FROM answers WHERE quest_id=?", (question_dic["id"],)
                )
                answers = await cursor.fetchall() #[<cursor.Row>,<cursor.Row>,<cursor.Row>,<cursor.Row>]
                answers_list = []
                correct_answer = ""
                for answer in answers:
                    answer_dic = dict(answer) # <cursor.Row> -> {'id':1, 'quest_id':1, 'text':'бобер','correct':0}
                    if answer_dic["correct"] == 1:
                        correct_answer = answer_dic["text"]
                    answers_list.append(answer_dic["text"])

                question_list.append(
                    {"question": question_dic["question"], "answers": answers_list, "correct_answer":correct_answer}
                )

    return question_list


# async def get_victorina(class_num: int, topic: str):
#     question_list = []
#     async with aiosqlite.connect("lead.db") as db:
#         db.row_factory = aiosqlite.Row
#         cursor = await db.execute(
#             "SELECT * FROM victorins WHERE topic = ? and class = ?", (topic, class_num)
#         )
#         victorina = await cursor.fetchone()  # ОБЪЕКТ КУРСОРА
#         if victorina:
#             victorina_dic = dict(victorina)
#             print(victorina_dic)
#             cursor = await db.execute(
#                 "SELECT * FROM questions WHERE vict_id=?", (victorina_dic["id"],)
#             )
#             questions = await cursor.fetchall()
#             for question in questions:
#                 question_dic = dict(question)
#                 question_list.append({'question':question_dic['question']})

#     #return question_list
