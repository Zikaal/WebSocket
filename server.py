import asyncio
import websockets
import json
import asyncpg
import bcrypt

MESSAGE_HISTORY_LIMIT = 10

async def get_message_history(conn):
    return await conn.fetch('''
        SELECT users.username, messages.message, messages.timestamp 
        FROM messages 
        JOIN users ON messages.user_id = users.id 
        ORDER BY messages.timestamp DESC 
        LIMIT $1
    ''', MESSAGE_HISTORY_LIMIT)

async def handler(websocket, path):
    conn = await asyncpg.connect(user='postgres', password='*******', database='chatdb', host='localhost')
    user_id = None

    try:
        async for message in websocket:
            if not message:
                continue  

            try:
                data = json.loads(message)

                if 'username' in data and 'password' in data:
                    username = data['username']
                    password = data['password'].encode('utf-8')
                    user = await conn.fetchrow('SELECT id, password FROM users WHERE username = $1', username)

                    if user:
                        stored_password = user['password'].encode('utf-8')
                        if bcrypt.checkpw(password, stored_password):
                            user_id = user['id']
                        else:
                            await websocket.send("Invalid password.")
                            await websocket.close()
                            return
                    else:
                        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
                        user_id = await conn.fetchval('INSERT INTO users(username, password) VALUES($1, $2) RETURNING id', username, hashed_password)

                    message_history = await get_message_history(conn)
                    for record in reversed(message_history):
                        history_message = f"{record['username']}: {record['message']}"
                        await websocket.send(history_message)

                elif 'message' in data and user_id:
                    await conn.execute('INSERT INTO messages(user_id, message) VALUES($1, $2)', user_id, data['message'])

            except json.JSONDecodeError:
                if user_id:
                    await conn.execute('INSERT INTO messages(user_id, message) VALUES($1, $2)', user_id, message)
                    await websocket.send(f"Received: {message}")
                else:
                    await websocket.send("Please register with a username and password first.")

    except Exception as e:
        print(f"Error: {e}")  

    finally:
        await conn.close()

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()

asyncio.run(main())


