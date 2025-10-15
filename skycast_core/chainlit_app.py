import chainlit as cl
import httpx
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Read backend URL from environment so Chainlit can call the backend running on port 8000
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Info card for assignment
INFO_LINK = "https://www.linkedin.com/school/pmaccelerator/"
DESCRIPTION = (
    "The Product Manager Accelerator Program supports PM professionals through every "
    "stage of their careers — from entry-level students to Directors. Our community is "
    "ambitious and committed, and members gain practical PM and leadership skills.\n\n"
    "Services include: PMA Pro (job placement & mock interviews), AI PM Bootcamp (build real AI products), "
    "PMA Power Skills (leadership & presentation training), PMA Leader (promotion coaching), and 1:1 Resume Review."
)

# Basic logging so you can see Chainlit activity in the terminal where you run Chainlit
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

@cl.on_chat_start
async def start():
    # Header message with author name and an Info button. Chainlit places messages in the chat flow;
    # an explicit top-right placement isn't supported via the Python API, so we show this near the header
    # as the first message users see.
    header = "🌤️ **Welcome to SkyCast AI!**\n\nType a city name to get current weather or 5-day forecast."
    # Make the LinkedIn page clickable from the header as a markdown link
    author_line = "**Built by Ali Arslan Khan** — [PM Accelerator](https://www.linkedin.com/company/product-manager-accelerator)"

    # Button that triggers a small info card explaining PM Accelerator
    buttons = [cl.Action(name="show_info", payload={}, label="Info")]

    await cl.Message(content=f"{header}\n\n{author_line}", actions=buttons).send()

@cl.on_message
async def get_weather(message: cl.Message):
    text = message.content.strip()

    if not text:
        await cl.Message(content="⚠️ Please enter a valid city name.").send()
        return

    # Ask user what they want
    buttons = [
        cl.Action(name="current", payload={"action": "current"}, label="Current Weather"),
        cl.Action(name="forecast", payload={"action": "forecast"}, label="5-Day Forecast")
    ]
    await cl.Message(
        content=f"What do you want to check for **{text}**?",
        actions=buttons
    ).send()

    cl.user_session.set("city", text)

@cl.action_callback("current")
async def show_current_weather(action: cl.Action):
    # Support payload-based actions: payload may contain the intended action name
    city = cl.user_session.get("city")
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{BACKEND_URL}/weather", params={"location": city}, timeout=10.0)
        except Exception as e:
            logger.exception("Error calling backend /weather")
            await cl.Message(content="❌ Could not reach backend to fetch current weather.").send()
            return
    try:
        data = res.json()
    except Exception:
        logger.error("Invalid JSON from backend /weather: %s", res.text)
        await cl.Message(content="❌ Unexpected response from backend.").send()
        return

    if data.get("error"):
        await cl.Message(content="❌ Could not fetch current weather.").send()
        return

    d = data["data"]
    msg = (
        f"**{d['name']} ({d['sys']['country']})**\n"
        f"🌡️ Temp: {d['main']['temp']} °C\n"
        f"💧 Humidity: {d['main']['humidity']}%\n"
        f"🌬️ Wind: {d['wind']['speed']} m/s\n"
        f"Condition: {d['weather'][0]['description'].capitalize()}"
    )
    await cl.Message(content=msg).send()

@cl.action_callback("forecast")
async def show_forecast(action: cl.Action):
    city = cl.user_session.get("city")
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{BACKEND_URL}/forecast", params={"location": city}, timeout=10.0)
        except Exception as e:
            logger.exception("Error calling backend /forecast")
            await cl.Message(content="❌ Could not reach backend to fetch forecast.").send()
            return
    try:
        data = res.json()
    except Exception:
        logger.error("Invalid JSON from backend /forecast: %s", res.text)
        await cl.Message(content="❌ Unexpected response from backend.").send()
        return

    if data.get("error"):
        await cl.Message(content="❌ Could not fetch forecast.").send()
        return

    lines = ["📅 **5-Day Forecast**:"]
    for day in data["forecast"]:
        lines.append(f"{day['date']}: {day['temp']} °C — {day['description'].capitalize()}")
    await cl.Message(content="\n".join(lines)).send()


@cl.action_callback("show_info")
async def show_info(action: cl.Action):
    # When the user clicks the Info button, show the short description and a link
    await cl.Message(
        content=(f"**PM Accelerator**\n\n{DESCRIPTION}\n\n"
                 f"More info: {INFO_LINK}" )
    ).send()
