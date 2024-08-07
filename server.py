import asyncio
import websockets
import json
import asyncpg

MESSAGE_HISTORY_LIMIT = 10

async def get_message_history(conn):
    return await conn.fetch('''
        SELECT users.username, messages.message, messages.timestamp 
        FROM messages 
        JOIN users ON messages.user_id = users.id 
        ORDER BY messages.timestamp DESC 
        LIMIT $1
    ''', MESSAGE_HISTORY_LIMIT)

async def handler(websocket,path):
    conn = await asyncpg.connect(user='postgres',password='Alikhan23012006',database='chatdb',host='localhost')
    user_id = None

    try:
        async for message in websocket:
            if not message:
                continue  

            try:
                data = json.loads(message)
                if 'username' in data:
                    username = data['username']
                    user = await conn.fetchrow('SELECT id FROM users WHERE username = $1', username)
                    if not user:
                        user_id = await conn.fetchval('INSERT INTO users(username) VALUES($1) RETURNING id', username)
                    else:
                        user_id = user['id']

                    # Send the last few messages to the new user
                    message_history = await get_message_history(conn)
                    for record in reversed(message_history):
                        history_message = f"{record['username']}: {record['message']}"
                        await websocket.send(history_message)

                elif 'message' in data and user_id:
                    # Сохраняем сообщение в базе данных
                    await conn.execute('INSERT INTO messages(user_id, message) VALUES($1, $2)', user_id, data['message'])

            except json.JSONDecodeError:
                # If message is not JSON, treat it as plain text
                if user_id:
                    await conn.execute('INSERT INTO messages(user_id, message) VALUES($1, $2)', user_id, message)
                    await websocket.send(f"Received: {message}")
                else:
                    await websocket.send("Please register with a username first.")

    except Exception as e:
        print(f"Error: {e}")  # Логируем ошибки на сервере

    finally:
        await conn.close()

async def main():
    async with websockets.serve(handler,"localhost","8765"):
        await asyncio.Future()

asyncio.run(main())
