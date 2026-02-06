from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import google

from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION

# 🔹 Import ALL tools
from tools import (
    get_weather,
    search_web,
    send_email,
    open_application,
    set_reminder,
    find_file,
    get_time,
    system_status,
    take_note,
    check_internet,
    daily_summary,
)

load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                voice="Aoede",
                temperature=0.4,  # faster, more controlled
            ),
            tools=[
                # 🌦️ Info tools
                get_weather,
                search_web,
                get_time,
                daily_summary,

                # 🧠 Productivity
                set_reminder,
                take_note,
                find_file,

                # 🖥️ System (safe)
                system_status,
                check_internet,
                open_application,

                # 📧 Sensitive (confirmation required)
                send_email,
            ],
        )


async def entrypoint(ctx: agents.JobContext):
    # 🔑 Always connect first
    await ctx.connect()

    session = AgentSession()

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            video_enabled=False,  # audio-only, low latency
        ),
    )

    await session.generate_reply(
        instructions=SESSION_INSTRUCTION,
    )


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint)
    )
