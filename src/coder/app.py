from operator import itemgetter

from typing import Optional, Dict

import chainlit as cl
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableConfig, Runnable
from langchain_openai import ChatOpenAI

from prompts import SYS_PROMPT


def setup_runnable():
    memory = cl.user_session.get("memory")  # type: ConversationBufferMemory
    model = ChatOpenAI(model="gpt-4.1-2025-04-14", streaming=True)
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
    cl.user_session.set("memory", ConversationBufferMemory(return_messages=True))
    setup_runnable()

    cl.user_session.set("chat_messages", [])

    # await open_editor()


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
