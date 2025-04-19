import asyncio
import chainlit as cl
from langchain_ollama import ChatOllama

model = ChatOllama(model="llama3.2:3b", temperature=0.4, num_ctx=2048)

def gen_to_async_iter(sync_iterable, delay=0):
    async def gen():
        for item in sync_iterable:
            yield item
            if delay:
                await asyncio.sleep(delay)
    return gen()

# Function to generate a blog with streaming to keep connection alive
async def generate_email_streaming(prompt_messages, prof_name):
    msg = cl.Message(content=f"⏳ Generating Email for: \n\n**{prof_name}**")
    await msg.send()
    
    generated_text = ""
    
    async def handle_token(token: str):
        nonlocal generated_text
        generated_text += token
        # Update the message every few tokens (say when its a multiple of 10) to avoid too many updates
        if len(token) > 0 and len(generated_text) % 10 == 0:
            msg.content = f"⏳ Generating: \n\n{generated_text}..."
            await msg.update()
            await asyncio.sleep(0.01)
    
    # Stream the response
    try:
        stream = model.stream(prompt_messages)
        stream = gen_to_async_iter(model.stream(prompt_messages), delay=0.01)
        async for chunk in stream:
            if chunk.content:
                await handle_token(chunk.content)
                await asyncio.sleep(0.01)

    except Exception as e:
        msg.content = f"❌ Error generating blog: {str(e)}"
        await msg.update()
        return None, msg
    
    return generated_text, msg