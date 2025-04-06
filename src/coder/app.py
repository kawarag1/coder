import chainlit as cl


async def open_editor():
    editor_props = {"lang": "python"}
    custom_element = cl.CustomElement(name="MyMonaco", props=editor_props, display="inline")
    await cl.ElementSidebar.set_title("canvas")
    await cl.ElementSidebar.set_elements([custom_element], key="editor-canvas")


@cl.action_callback("close_editor")
async def on_test_action():
    await cl.ElementSidebar.set_elements([])


@cl.on_chat_start
async def on_start():
    cl.user_session.set("chat_messages", [])

    await open_editor()
