import re
import uuid
from operator import itemgetter

from typing import Optional, Dict, List

import chainlit as cl
from chainlit.types import CommandDict
from gitingest import ingest
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableConfig, Runnable
from langchain_openai import ChatOpenAI
from starlette.config import environ

from prompts import SYS_PROMPT
from tochka_client import TochkaClient

commands = [
    CommandDict(id="github", description="Помоги разобраться с github репозиторием", icon="image", button=False,
                persistent=False),
    CommandDict(id="purchase", description="Оплатить подписку", icon="image", button=False, persistent=False),
]


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

    cl.user_session.set("memory", ConversationBufferMemory(return_messages=True))
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
    if message.command == "purchase":
        payment_link = await generate_payment_link()
        await cl.Message(content=f"[Ссылка на оплату]({payment_link})").send()
        return
    elif message.command == "github":
        content = message.content
        pattern: str = r'(https?://(?:www\.)?github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(?:/)?'
        matches: List[str] = re.findall(pattern, content)
        if len(matches) == 0:
            await cl.Message(content="Повтори комманду со ссылкой на репозиторий").send()
            return
        if len(matches) > 1:
            await cl.Message(
                content="Больше одного репозитория... Выбери только один, а то будет какая-то каша.").send()
            return
        # return matches
        summary, tree, content = ingest(source=matches[0])
        memory = cl.user_session.get("memory")  # type: ConversationBufferMemory
        runnable = cl.user_session.get("runnable")  # type: Runnable
        await runnable.ainvoke(
                {"question": content},
                config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
        )
        memory.chat_memory.add_user_message(content)
        info = parse_repository_info(summary)
        await cl.Message(content=f"Проанализирован репозиторий {info['repository']}").send()
        return
    memory = cl.user_session.get("memory")  # type: ConversationBufferMemory

    runnable = cl.user_session.get("runnable")  # type: Runnable

    res = cl.Message(content="")

    async for chunk in runnable.astream(
            {"question": message.content},
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await res.stream_token(chunk)

    await res.send()

    memory.chat_memory.add_user_message(message.content)
    memory.chat_memory.add_ai_message(res.content)


async def generate_payment_link():
    client = TochkaClient(environ.get('TOCHKA_API_TOKEN'), environ.get('TOCHKA_CUSTOMER_CODE'),
                          environ.get('TOCHKA_SUCCESS_REDIRECT_URL'), environ.get('TOCHKA_FAILURE_REDIRECT_URL'))
    response = await client.create_payment_link('1000', str(uuid.uuid4()))
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
