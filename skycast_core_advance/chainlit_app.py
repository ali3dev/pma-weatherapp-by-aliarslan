import chainlit as cl
import httpx, os
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# ----------------------------------------------------------
# Greeting
# ----------------------------------------------------------
@cl.on_chat_start
async def start():
    await cl.Message(
        author="SkyCast",
        content=(
            "## 🌤️ Welcome to **SkyCast AI**\n"
            "_Your personal weather assistant powered by FastAPI + Chainlit._\n\n"
            "**You can type:**\n"
            "• 🏙️ City or Town name\n"
            "• 📮 ZIP / Postal Code (e.g. `94040,US`)\n"
            "• 🧭 GPS Coordinates (e.g. `31.5497,74.3436`)\n\n"
            "Then choose what you’d like to check 👇"
        ),
    ).send()

# ----------------------------------------------------------
# Message Handler
# ----------------------------------------------------------
@cl.on_message
async def get_weather(message: cl.Message):
    # Handle flows initiated by history actions
    expecting_update_id = cl.user_session.get("expecting_update_id")
    if expecting_update_id:
        # User should send an ID to update
        try:
            rid = int(message.content.strip())
        except Exception:
            await cl.Message(content="⚠️ Please send a valid numeric record ID to update.").send()
            return

        cl.user_session.set("expecting_update_id", None)
        cl.user_session.set("update_id", rid)
        await cl.Message(content=f"Send the new description for record {rid}.").send()
        return

    expecting_delete_id = cl.user_session.get("expecting_delete_id")
    if expecting_delete_id:
        s = message.content.strip()
        if not s:
            await cl.Message(content="⚠️ Please send at least one numeric ID to delete.").send()
            return

        # parse comma-separated ids and ranges like 4-6
        ids = set()
        parts = [p.strip() for p in s.split(',') if p.strip()]
        for part in parts:
            if '-' in part:
                try:
                    a, b = part.split('-', 1)
                    a_i = int(a.strip())
                    b_i = int(b.strip())
                    if a_i <= b_i:
                        for x in range(a_i, b_i + 1):
                            ids.add(x)
                    else:
                        for x in range(b_i, a_i + 1):
                            ids.add(x)
                except Exception:
                    # skip invalid range
                    continue
            else:
                try:
                    ids.add(int(part))
                except Exception:
                    continue

        if not ids:
            await cl.Message(content="⚠️ No valid IDs found in your input.").send()
            return

        # Ask for confirmation before deleting
        cl.user_session.set("expecting_delete_id", None)
        cl.user_session.set("pending_delete_ids", sorted(ids))

        ids_list = ", ".join(str(i) for i in sorted(ids))
        buttons = [
            cl.Action(name="confirm_delete", payload={"value": "confirm_delete"}, label="✅ Confirm Delete"),
            cl.Action(name="cancel_delete", payload={"value": "cancel_delete"}, label="❌ Cancel")
        ]

        await cl.Message(content=f"You are about to delete these records: {ids_list}\nDo you want to proceed?", actions=buttons).send()
        return

    # If user is in update mode, treat incoming message as the new description
    update_id = cl.user_session.get("update_id")
    if update_id:
        new_desc = message.content.strip()
        if not new_desc:
            await cl.Message(content="⚠️ Please send a non-empty description to update the record.").send()
            return

        async with httpx.AsyncClient() as client:
            # weather_routes.update_weather uses PUT /update/{record_id}?desc=...
            res = await client.put(f"{BACKEND_URL}/update/{update_id}", params={"desc": new_desc})

        cl.user_session.set("update_id", None)
        if res.status_code == 200:
            await cl.Message(content=f"✅ Record {update_id} updated.").send()
        else:
            await cl.Message(content=f"❌ Failed to update record {update_id}.").send()
        return

    # Date-range flow: expecting start/end dates
    # Check these BEFORE treating the message as a location so date inputs
    # won't be stored as the session city.
    expecting_range_start = cl.user_session.get("expecting_range_start")
    if expecting_range_start:
        start_date = message.content.strip()
        cl.user_session.set("expecting_range_start", None)
        cl.user_session.set("range_start", start_date)
        cl.user_session.set("expecting_range_end", True)
        await cl.Message(content="Please send the end date (YYYY-MM-DD) for the range.").send()
        return

    expecting_range_end = cl.user_session.get("expecting_range_end")
    if expecting_range_end:
        end_date = message.content.strip()
        start_date = cl.user_session.get("range_start")
        cl.user_session.set("expecting_range_end", None)
        cl.user_session.set("range_start", None)

        # Use the current city in session as the location for the range
        location = cl.user_session.get("city") or message.content.strip()
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{BACKEND_URL}/create_range", params={"location": location, "start_date": start_date, "end_date": end_date})

        if res.status_code == 200:
            j = res.json()
            if j.get("error"):
                await cl.Message(content=f"❌ Could not create range: {j.get('message')}").send()
            else:
                await cl.Message(content=f"✅ {j.get('message')}").send()
        else:
            await cl.Message(content=f"❌ Failed to create range (status {res.status_code}).").send()
        return

    city = message.content.strip()
    if not city:
        await cl.Message(content="⚠️ Please enter a valid location.").send()
        return

    cl.user_session.set("city", city)
    buttons = [
        # Newer Chainlit Action model requires a `payload` field (validated by pydantic).
        # Provide a small payload dict with the action value so validation passes.
        cl.Action(name="current", payload={"value": "current"}, label="☀️ Current Weather"),
        cl.Action(name="forecast", payload={"value": "forecast"}, label="🗓️ 5-Day Forecast"),
        cl.Action(name="export", payload={"value": "export"}, label="📦 Download Data")
        ,
        cl.Action(name="history", payload={"value": "history"}, label="📜 History"),
        cl.Action(name="create_range", payload={"value": "create_range"}, label="➕ Create Date Range Records")
    ]
    await cl.Message(content=f"**Location:** {city}\nWhat do you want to do?", actions=buttons).send()

# ----------------------------------------------------------
# Current Weather
# ----------------------------------------------------------
@cl.action_callback("current")
async def show_current_weather(action: cl.Action):
    city = cl.user_session.get("city")
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{BACKEND_URL}/weather", params={"location": city})
    data = res.json()

    if data.get("error"):
        await cl.Message(content="❌ Could not fetch current weather.").send()
        return

    d = data["data"]
    msg = (
        f"### 🌍 {d['name']} ({d['sys']['country']})\n"
        f"🌡️ **Temp:** {d['main']['temp']} °C\n"
        f"💧 **Humidity:** {d['main']['humidity']} %\n"
        f"🌬️ **Wind:** {d['wind']['speed']} m/s\n"
        f"☁️ **Condition:** {d['weather'][0]['description'].capitalize()}"
    )
    await cl.Message(content=msg).send()

# ----------------------------------------------------------
# 5-Day Forecast
# ----------------------------------------------------------
@cl.action_callback("forecast")
async def show_forecast(action: cl.Action):
    city = cl.user_session.get("city")
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{BACKEND_URL}/forecast", params={"location": city})
    data = res.json()

    if data.get("error"):
        await cl.Message(content="❌ Could not fetch forecast.").send()
        return

    lines = ["### 🗓️ 5-Day Forecast:"]
    for day in data["forecast"]:
        lines.append(f"{day['date']} → {day['temp']} °C — {day['description'].capitalize()}")
    await cl.Message(content="\n".join(lines)).send()

# ----------------------------------------------------------
# Export Data
# ----------------------------------------------------------
@cl.action_callback("export")
async def handle_export(action: cl.Action):
    # We'll fetch the exported files (binary) and attach them to the Chainlit message
    # so users can download directly from the chat UI. Backend endpoints remain unchanged.
    endpoints = [
        ("json", f"{BACKEND_URL}/export/json"),
        ("csv",  f"{BACKEND_URL}/export/csv"),
        ("pdf",  f"{BACKEND_URL}/export/pdf"),
    ]

    files_to_send = []
    msgs = []

    async with httpx.AsyncClient() as client:
        for ext, url in endpoints:
            # Request the endpoint. If it returns JSON with message only, fallback to asking for the file path.
            # Many backends will return the exported file directly (binary) or a JSON with message.
            res = await client.get(url)

            if res.status_code != 200:
                msgs.append(f"Failed to export {ext.upper()}")
                continue

            # Try to parse as JSON first to see if backend responded with metadata
            try:
                j = res.json()
            except Exception:
                j = None

            if j and isinstance(j, dict) and j.get("message") and not res.headers.get("content-type", "").startswith("application/"):
                # Backend returned a JSON message (likely created file on server). We'll attempt to read that file
                msgs.append(j.get("message"))
                filename = f"exports/weather_records.{ext}"
                if os.path.exists(filename):
                    # Ensure we attach the actual file by path so Chainlit shows a download link
                    files_to_send.append(os.path.abspath(filename))
                continue

            # If response is binary (file), attach directly
            content_type = res.headers.get("content-type", "application/octet-stream")
            disposition = res.headers.get("content-disposition", "")
            # Try to deduce filename
            filename = None
            if "filename=" in disposition:
                filename = disposition.split("filename=")[-1].strip('"')
            if not filename:
                filename = f"weather_records.{ext}"

            data = res.content
            msgs.append(f"Exported file: {filename}")
            # Write the response bytes to the exports folder so we can attach by path
            os.makedirs("exports", exist_ok=True)
            file_path = os.path.join("exports", filename)
            with open(file_path, "wb") as fh:
                fh.write(data)
            files_to_send.append(os.path.abspath(file_path))

    # Send a message with the export summary and attached files (if any)
    content = "✅ Export complete.\n\nYou can download the exported files below.\n\n" + "\n".join(f"• {m}" for m in msgs)

    if files_to_send:
        # Convert absolute file paths into cl.File objects by path so Chainlit shows download links.
        cl_files = []
        for p in files_to_send:
            try:
                cf = cl.File(name=os.path.basename(p), path=p)
                cl_files.append(cf)
            except Exception:
                # If creating cl.File fails for any reason, skip attaching that file but keep others
                pass

        # Send the message with file attachments (if any)
        if cl_files:
            # Send the summary message first, then send each file so the UI shows download links
            await cl.Message(content=content).send()
            for cf in cl_files:
                try:
                    await cf.send()
                except Exception:
                    # If sending a specific file fails, continue with others
                    pass
            return
        else:
            # No attachments possible, still send the summary message
            await cl.Message(content=content).send()
            return

    # If no files to send, just send the summary message
    await cl.Message(content=content).send()


# ----------------------------------------------------------
# History / CRUD via Chainlit
# ----------------------------------------------------------
@cl.action_callback("history")
async def show_history(action: cl.Action):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{BACKEND_URL}/records")
    data = res.json()

    if data.get("count") == 0:
        await cl.Message(content="No history records found.").send()
        return

    lines = ["### 📜 History:"]
    for r in data.get("records", []):
        lines.append(f"ID {r['id']} — {r['city']} — {r['temp']} °C — {r['desc']}")

    # Actions for update/delete (user selects an ID manually by typing it after pressing Update)
    buttons = [
        cl.Action(name="start_update", payload={"value": "start_update"}, label="✏️ Update Record"),
        cl.Action(name="delete_record", payload={"value": "delete_record"}, label="🗑️ Delete Record")
    ]

    await cl.Message(content="\n".join(lines), actions=buttons).send()


@cl.action_callback("create_range")
async def start_create_range(action: cl.Action):
    await cl.Message(content="Please send the start date (YYYY-MM-DD) for the range.").send()
    cl.user_session.set("expecting_range_start", True)



@cl.action_callback("start_update")
async def start_update(action: cl.Action):
    # Ask user to send the ID to update (e.g. '5') — then we'll prompt for new description
    await cl.Message(content="Please send the ID of the record you want to update (e.g. 5).").send()
    # Set a short-lived session flag to indicate next message should contain the ID to update
    cl.user_session.set("expecting_update_id", True)


@cl.action_callback("delete_record")
async def delete_record(action: cl.Action):
    await cl.Message(content="Please send the ID or IDs of the record(s) you want to delete (e.g. `5` or `1,2,3` or ranges like `4-6`).").send()
    cl.user_session.set("expecting_delete_id", True)


@cl.action_callback("confirm_delete")
async def confirm_delete(action: cl.Action):
    pending = cl.user_session.get("pending_delete_ids") or []
    if not pending:
        await cl.Message(content="No pending deletions.").send()
        return

    deleted = []
    failed = {}
    # Use backend batch delete endpoint for efficiency
    ids_param = ",".join(str(i) for i in pending)
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(f"{BACKEND_URL}/delete_batch", params={"ids": ids_param})
        except Exception as e:
            await cl.Message(content=f"❌ Batch delete request failed: {e}").send()
            cl.user_session.set("pending_delete_ids", None)
            return

        if res.status_code == 200:
            try:
                j = res.json()
            except Exception:
                j = None

            if j and not j.get("error") and j.get("result"):
                deleted = j["result"].get("deleted", [])
                failed = j["result"].get("failed", {})
            else:
                await cl.Message(content=f"❌ Batch delete failed: {j}").send()
                cl.user_session.set("pending_delete_ids", None)
                return
        else:
            await cl.Message(content=f"❌ Batch delete failed: status {res.status_code}").send()
            cl.user_session.set("pending_delete_ids", None)
            return

    cl.user_session.set("pending_delete_ids", None)

    parts_out = []
    if deleted:
        parts_out.append("Deleted: " + ",".join(str(i) for i in deleted))
    if failed:
        parts_out.append("Failed: " + ", ".join(f"{i} ({failed[i]})" for i in failed))

    await cl.Message(content="\n".join(parts_out) if parts_out else "No deletions performed.").send()


@cl.action_callback("cancel_delete")
async def cancel_delete(action: cl.Action):
    cl.user_session.set("pending_delete_ids", None)
    await cl.Message(content="Deletion cancelled.").send()
