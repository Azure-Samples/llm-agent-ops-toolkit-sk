import os
import io
import wave
import numpy as np
import audioop
import tempfile
import sys
from dotenv import load_dotenv
import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from chainlit.input_widget import TextInput
from chainlit.step import Step
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.connectors.ai.open_ai import AzureAudioToText, AzureTextToAudio, OpenAITextToAudioExecutionSettings
from semantic_kernel.contents import AudioContent

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
load_dotenv(override=True)

# The following imports having dependencies on the environment variables
from src.mysql.execution_env import SqlEnv
from src.groupchat.state_flow_chat import get_chat_client
from exp_src.persistence.database_setup import DataPersistence
from exp_src.customization.actions import CustomActions

sql_executor_env = SqlEnv.get_sql_executor_env_from_environment()
data_persistence = DataPersistence(enable_storage_provider=False)

# Define a threshold for detecting silence and a timeout for ending a turn
SILENCE_THRESHOLD = 3500 # Adjust based on your audio level (e.g., lower for quieter audio)
SILENCE_TIMEOUT = 1300.0 # Seconds of silence to consider the turn finished

text_to_audio_service = AzureTextToAudio(deployment_name="tts")
audio_to_text_service = AzureAudioToText(deployment_name="whisper")

@cl.data_layer
def get_data_layer():
    return SQLAlchemyDataLayer(
        conninfo=data_persistence.get_connection_url_async(),
        storage_provider=data_persistence.get_storage_provider(),
    )


@cl.password_auth_callback
def password_auth_callback(username: str, password: str) -> bool:
    if (username == os.environ["CHAINLIT_USERNAME"]) and (
        password == os.environ["CHAINLIT_PASSWORD"]
    ):
        return cl.User(
            identifier=username,
            metadata={"role": os.environ["CHAINLIT_ROLE"], "provider": "credentials"},
        )
    return None


@cl.action_callback("thumbs_up_action")
async def thumbs_up_action_callback(action: cl.Action) -> None:
    await CustomActions.thumbs_up_down_action_handler(
        message_id=action.payload["message_id"],
        thread_id=action.payload["thread_id"],
        value=action.payload["value"],
        data_layer=get_data_layer(),
    )


@cl.action_callback("thumbs_down_action")
async def thumbs_down_action_callback(action: cl.Action) -> None:
    await CustomActions.thumbs_up_down_action_handler(
        message_id=action.payload["message_id"],
        thread_id=action.payload["thread_id"],
        value=action.payload["value"],
        data_layer=get_data_layer(),
    )


@cl.on_settings_update
async def setting_update(settings):
    cl.context.session.chat_settings = settings


@cl.on_chat_start
async def start_chat():
    print("=================Chat started================")
    sql_executor_env.connect()
    global chat
    chat = get_chat_client(sql_executor_env)
    await cl.ChatSettings(
        [
            TextInput(
                id="experiment",
                label="Experiment",
                placeholder="Mention Experiment Name",
                initial="SQL Copilot Experiment",
                tooltip="Name of the experiment",
            )
        ]
    ).send()

@cl.on_audio_start
async def on_audio_start():
    cl.user_session.set("silent_duration_ms", 0)
    cl.user_session.set("is_speaking", False)
    cl.user_session.set("audio_chunks", [])
    return True

@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.InputAudioChunk):
    audio_chunks = cl.user_session.get("audio_chunks")
    
    if audio_chunks is not None:
        audio_chunk = np.frombuffer(chunk.data, dtype=np.int16)
        audio_chunks.append(audio_chunk)

    # If this is the first chunk, initialize timers and state
    if chunk.isStart:
        cl.user_session.set("last_elapsed_time", chunk.elapsedTime)
        cl.user_session.set("is_speaking", True)
        return

    audio_chunks = cl.user_session.get("audio_chunks")
    last_elapsed_time = cl.user_session.get("last_elapsed_time")
    silent_duration_ms = cl.user_session.get("silent_duration_ms")
    is_speaking = cl.user_session.get("is_speaking")

    # Calculate the time difference between this chunk and the previous one
    time_diff_ms = chunk.elapsedTime - last_elapsed_time
    cl.user_session.set("last_elapsed_time", chunk.elapsedTime)

    # Compute the RMS (root mean square) energy of the audio chunk
    audio_energy = audioop.rms(chunk.data, 2)  # Assumes 16-bit audio (2 bytes per sample)

    if audio_energy < SILENCE_THRESHOLD:
        # Audio is considered silent
        silent_duration_ms += time_diff_ms
        cl.user_session.set("silent_duration_ms", silent_duration_ms)
        if silent_duration_ms >= SILENCE_TIMEOUT and is_speaking:
            cl.user_session.set("is_speaking", False)
            await process_audio()
    else:
        # Audio is not silent, reset silence timer and mark as speaking
        cl.user_session.set("silent_duration_ms", 0)
        if not is_speaking:
            cl.user_session.set("is_speaking", True)

async def process_audio():
    # Get the audio buffer from the session
    if audio_chunks:=cl.user_session.get("audio_chunks"):
       # Concatenate all chunks
        concatenated = np.concatenate(list(audio_chunks))
        
        # Create an in-memory binary stream
        wav_buffer = io.BytesIO()
        
        # Create WAV file with proper parameters
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # mono
            wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
            wav_file.setframerate(24000)  # sample rate (24kHz PCM)
            wav_file.writeframes(concatenated.tobytes())
        
        # Reset buffer position
        wav_buffer.seek(0)
        
        cl.user_session.set("audio_chunks", [])

    frames = wav_file.getnframes()
    rate = wav_file.getframerate()

    duration = frames / float(rate)  
    if duration <= 1.71:
        print("The audio is too short, please try again.")
        return

    audio_buffer = wav_buffer.getvalue()

    input_audio_el = cl.Audio(content=audio_buffer, mime="audio/wav")

    with open(tempfile.NamedTemporaryFile(suffix=".wav").name, "wb") as f:
        f.write(audio_buffer)
        whisper_input = f.name
        user_input = await audio_to_text_service.get_text_content(AudioContent.from_audio_file(whisper_input))
        transcription = user_input.text

    message = await cl.Message(
        author="You", 
        type="user_message",
        content=transcription,
        elements=[input_audio_el]
    ).send()

    async with Step(name="on_message", type="run", parent_id=message.id) as s:
        s.input = message
        final_response = await run_team(transcription)
        final_response = ''.join(e for e in final_response if e.isalnum() or e.isspace())
        audio_content = await text_to_audio_service.get_audio_content(
            final_response, OpenAITextToAudioExecutionSettings(response_format="wav")
        )
        audio_stream = io.BytesIO(audio_content.data)
        output_audio_el = cl.Audio(
            auto_play=True,
            mime="audio/wav",
            content=audio_stream.read(),
        )
        await cl.Message(content=final_response, elements=[output_audio_el]).send()

async def run_team(query: str):
    query_with_init_thought = sql_executor_env.attach_init_observation(query)
    await chat.add_chat_message(
        ChatMessageContent(role=AuthorRole.USER, content=query_with_init_thought)
    )
    cl_msg = cl.Message(
        content=f"{AuthorRole.USER.upper()}: init: {query_with_init_thought}",
        author=AuthorRole.USER,
    )
    await cl_msg.send()

    async for content in chat.invoke():
        message_metadata = {
            "experiment": cl.context.session.chat_settings.get("experiment", None)
        }
        cl_msg = cl.Message(
            content=f"{content.role.upper()} - {content.name or '*'}: {content.content}",
            author=content.name,
            metadata=message_metadata,
        )
        sent_message = await cl_msg.send()
        if not chat.is_complete:
            current_thread_id = cl.context.current_run.thread_id
            custom_actions = CustomActions(
                message_id=sent_message.id, thread_id=current_thread_id
            )
            cl_msg.actions = [
                custom_actions.get_thumbs_up_action(),
                custom_actions.get_thumbs_down_action(),
            ]
            await cl_msg.update()
        final_response = content.content
    return final_response

@cl.on_message
async def run_chat(message: cl.Message):
    await run_team(message.content)


@cl.on_chat_end
async def end_chat():
    print("=================Chat ended==================")
    chat.is_complete = True
    sql_executor_env.close()


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Simple Query",
            message="What is the total amount of sales so far?",
        ),
        cl.Starter(
            label="Simple Query with Join",
            message="List all product line along the number of orders placed for each product line.",
        ),
        cl.Starter(
            label="Complex Query with 3 joins",
            message="How many employees are placing orders?",
        ),
        cl.Starter(
            label="Irrelevant Query",
            message="What is latest stock price of Microsoft?",
        ),
    ]
