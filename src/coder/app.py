import re
import uuid
import os
from operator import itemgetter

from typing import Optional, Dict, List

import chainlit as cl
from chainlit.types import CommandDict
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from gitingest import ingest
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableConfig, Runnable
from langchain_openai import ChatOpenAI
from starlette.config import environ
from database.database import get_session, get_engine
from models.models import Subscription, Payment, User, SubTypes
from sqlalchemy import insert, select, update
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from prompts import SYS_PROMPT
from tochka_client import TochkaClient
from database.database import create_tables

commands = [
    CommandDict(id="github", description="Помоги разобраться с github репозиторием", icon="image", button=False,
                persistent=False),
    CommandDict(id="purchase", description="Оплатить подписку", icon="image", button=False, persistent=False),
    CommandDict(id="mysub", description="Моя подписка", icon="image", button=False, persistent=False)
]

@cl.on_app_startup
async def start():
    await create_tables()

@cl.data_layer
def change_data_layer():
    return SQLAlchemyDataLayer(conninfo = os.getenv("SQLDATABASE_URL"))

def setup_runnable():
    memory = cl.user_session.get("memory")  # type: ConversationBufferMemory
    model = ChatOpenAI(model="gpt-4.1-2025-04-14", base_url="https://api.proxyapi.ru/openai/v1", streaming=True)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYS_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )
    runnable = (
            RunnablePassthrough.assign(
                history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
            )
            | prompt
            | model
            | StrOutputParser()
    )
    cl.user_session.set("runnable", runnable)


async def open_editor():
    editor_props = {"lang": "python"}
    custom_element = cl.CustomElement(name="MyMonaco", props=editor_props, display="inline")
    await cl.ElementSidebar.set_title("canvas")
    await cl.ElementSidebar.set_elements([custom_element], key="editor-canvas")


@cl.action_callback("close_editor")
async def on_close_editor():
    await cl.ElementSidebar.set_elements([])


@cl.on_chat_start
async def on_start():
    # enable commands
    await cl.context.emitter.set_commands(commands)

    memory = ConversationBufferMemory(return_messages=True)
    cl.user_session.set("memory", memory)
    setup_runnable()

    cl.user_session.set("chat_messages", [])

    # uncomment when subscription will be persisted
    # if False:
    #     actions = [
    #         cl.Action(name="renew_subscription_button", payload={"value": "example_value"}, label="Оформить подписку")
    #     ]
    #     await cl.Message(content="У вас закончился пробный период", actions=actions).send()
    # await open_editor()


@cl.action_callback("renew_subscription_button")
async def on_action(action):
    payment_link = await generate_payment_link()
    await cl.Message(content=f"[Ссылка на оплату]({payment_link})").send()
    # Optionally remove the action button from the chatbot user interface
    await action.remove()


# `on_resume` impl is required for the chat history feature and more
@cl.on_chat_resume
async def on_chat_resume(thread):
    memory = ConversationBufferMemory(return_messages=True)
    root_messages = [m for m in thread["steps"] if m["parentId"] is None]
    for message in root_messages:
        if message["type"] == "user_message":
            memory.chat_memory.add_user_message(message["output"])
        else:
            memory.chat_memory.add_ai_message(message["output"])

    cl.user_session.set("memory", memory)

    setup_runnable()


@cl.on_message
async def on_message(message: cl.Message):
    try:
        root_msg = cl.Message(
            content="⌛️ Обработка запроса...",
            author="system"
        )
        await root_msg.send()
        
        memory = cl.user_session.get("memory")
        runnable = cl.user_session.get("runnable")
        memory.chat_memory.add_user_message(message.content)

        if message.command and message.command.lower() == "mysub":
            memory.chat_memory.add_ai_message(root_msg.content)
            await show_sub_status(memory, root_msg.id)
            return

        elif message.command == "purchase":
            await create_sub()
            return

        elif message.command == "github":
            memory.chat_memory.add_ai_message(root_msg.content)
            content = message.content
            pattern = r'(https?://(?:www\.)?github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(?:/)?'
            matches = re.findall(pattern, content)
            
            second_root_msg = cl.Message(
                content="⌛️ Анализирую ссылку...",
                author="system"
            )
            await second_root_msg.send()
            memory.chat_memory.add_ai_message(second_root_msg.content)

            if not matches:
                errMessage = cl.Message(
                    content="Повторите команду со ссылкой на репозиторий"
                )
                await errMessage.send()
                memory.chat_memory.add_ai_message(errMessage.content)
                return
            
            if len(matches) > 1:
                errMessage = cl.Message(
                    content="Пожалуйста, укажите только один репозиторий"
                )
                await errMessage.send()
                memory.chat_memory.add_ai_message(errMessage.content)
                return

            github_msg = cl.Message(
                content="Анализирую репозиторий..."
            )
            await github_msg.send()

            summary, tree, content = ingest(source=matches[0])
            await runnable.ainvoke(
                {"question": content},
                config=RunnableConfig(
                    callbacks=[cl.LangchainCallbackHandler(
                        stream_final_answer=True,
                        answer_prefix_tokens=["FINAL", "ANSWER"]
                    )]
                ),
            )
            
            memory.chat_memory.add_user_message(content)
            info = parse_repository_info(summary)
            result_msg = cl.Message(
                content=f"Проанализирован репозиторий {info['repository']}"
            )
            await result_msg.send()
            memory.chat_memory.add_ai_message(result_msg.content)
            return

        res = cl.Message(content="")
        
        async for chunk in runnable.astream(
            {"question": message.content},
            config=RunnableConfig(
                callbacks=[cl.LangchainCallbackHandler(
                    stream_final_answer=True,
                    answer_prefix_tokens=["FINAL", "ANSWER"]
                )]
            ),
        ):
            await res.stream_token(chunk)
        
        await res.send()
        memory.chat_memory.add_ai_message(res.content)

    except Exception as e:    
        error_msg = cl.Message(content=f"❌ Ошибка: {str(e)}")
        await error_msg.send()
        raise


async def generate_payment_link():
    client = TochkaClient(environ.get('TOCHKA_API_TOKEN'), environ.get('TOCHKA_CUSTOMER_CODE'),
                          environ.get('TOCHKA_SUCCESS_REDIRECT_URL'), environ.get('TOCHKA_FAILURE_REDIRECT_URL'))
    response = await client.create_payment_link('1000', str(uuid.uuid4()))
    payment_link = response['paymentLink']
    return payment_link

async def generate_sandbox_payment_link():
    client = TochkaClient(environ.get('TOCHKA_API_TOKEN'), environ.get('TOCHKA_CUSTOMER_CODE'),
                          environ.get('TOCHKA_SUCCESS_REDIRECT_URL'), environ.get('TOCHKA_FAILURE_REDIRECT_URL'))
    response = await client.create_payment_link_sandbox("1234.12", str(uuid.uuid4()))
    payment_link = response['paymentLink']
    return payment_link

# noinspection PyUnusedLocal
@cl.oauth_callback
def oauth_callback(
        provider_id: str,
        token: str,
        raw_user_data: Dict[str, str],
        default_user: cl.User,
) -> Optional[cl.User]:
    # save this 'token' to use it later for some API calls
    default_user.metadata['token'] = token
    return default_user


# Util
def parse_repository_info(info: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in info.splitlines():
        if not line.strip():
            continue
        key, value = line.strip().split(":", 1)
        key = key.strip().lower().replace(' ', '_')
        value = value.strip()
        result[key] = value
    return result

#show user's sub status
async def show_sub_status(memory: ConversationBufferMemory, parentID):
    user = cl.user_session.get("user")
    if not user:
        message = cl.Message(content="Не удалось определить пользователя", parent_id=parentID) 
        memory.chat_memory.add_ai_message(message.content)
        await message.send()
        return

    async with await get_session() as db_session:
        try:
           
            user_id = user.id if isinstance(user.id, uuid.UUID) else uuid.UUID(user.id)
            
            stmt = select(Subscription).where(
                Subscription.userId == user_id,  
                Subscription.endsAt >= datetime.now()
            ).order_by(Subscription.endsAt.desc()).limit(1)

            result = await db_session.execute(stmt)
            subscription = result.scalars().first()

            if not subscription:
                message = cl.Message(content="У вас нет активной подписки. Для оформления используйте команду '/purchase' ", parent_id=parentID)
                print(f"New message: {message.id}, parent: {message.parent_id}")
                memory.chat_memory.add_ai_message(message.content)
                await message.send()
                return

            
            sub_type_stmt = select(SubTypes).where(SubTypes.id == subscription.subTypeId)
            sub_type_result = await db_session.execute(sub_type_stmt)
            sub_type = sub_type_result.scalars().first()

            message = f"""
            **Статус вашей подписки:**
            - Тип: {sub_type.title if sub_type else 'Неизвестно'}
            - Стоимость: {sub_type.cost if sub_type else 'Неизвестно'} руб.
            - Начало: {subscription.startsAt.strftime('%d.%m.%Y')}
            - Окончание: {subscription.endsAt.strftime('%d.%m.%Y')}
            - Автопродление: {'Да' if subscription.autoRenew else 'Нет'}
            """

            await cl.Message(content=message, parent_id=parentID).send()

        except Exception as e:
            await cl.Message(content=f"Ошибка при получении статуса подписки: {str(e)}").send()


async def create_sub():
    user = cl.user_session.get("user")
    if not user:
        message = cl.Message(content="Не удалось определить пользователя") 
        await message.send()
        return
    async with await get_session() as db_session:
        user_id = user.id if isinstance(user.id, uuid.UUID) else uuid.UUID(user.id)

        check_query = select(Subscription).filter(Subscription.userId == user_id)
        result = (await db_session.execute(check_query))
        sub = result.scalars().all()
        print(sub)
        if sub == []:
            IdForPayment = uuid.uuid4()
            payment_query = insert(Payment).values(
            id = IdForPayment,
            amount = 100,
            operationId = "975f3eef-e6bb-4e3c-8fa6-45132c2e6a9c"
            )
            await db_session.execute(payment_query)

            
            query = insert(Subscription).values(
                userId = user_id,
                subTypeId = "4ab28f9c-5e1d-4f3a-8b7c-1d6e5f3a9b8c",
                paymentId = IdForPayment,
                startsAt = datetime.utcnow(),
                endsAt = datetime.utcnow() + timedelta(days=30),
                autoRenew = True
            )
            await db_session.execute(query)
            await db_session.commit()
            await cl.Message(content = "Подписка оформлена!").send()
        else:
            await cl.Message(content="У вас уже есть подписка!").send()
            return