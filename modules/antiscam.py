from .. import loader, utils
import re
from datetime import datetime

@loader.tds
class AntiScamMod(loader.Module):
    """Anti-Scam + Evidence Logger"""

    strings = {"name": "AntiScam"}

    def __init__(self):
        self.db = {}

        self.bad_words = [
            "invest", "crypto", "profit", "giveaway",
            "airdrop", "earn money", "btc", "usdt"
        ]

        self.link_regex = re.compile(r"(https?://|t\.me/|bit\.ly/|tinyurl\.com)")

    async def watcher(self, message):
        if not message.text:
            return

        text = message.text.lower()
        suspicious = False

        for word in self.bad_words:
            if word in text:
                suspicious = True

        if self.link_regex.search(text):
            suspicious = True

        if not suspicious:
            return

        user = await message.get_sender()
        user_id = user.id

        if user_id not in self.db:
            self.db[user_id] = []

        self.db[user_id].append({
            "text": message.text,
            "chat": message.chat_id,
            "msg_id": message.id,
            "time": str(datetime.now())
        })

    async def reportcmd(self, message):
        args = utils.get_args_raw(message)

        if not args:
            await utils.answer(message, "Укажи пользователя")
            return

        try:
            user = await message.client.get_entity(args)
        except:
            await utils.answer(message, "Не найден")
            return

        user_id = user.id

        if user_id not in self.db:
            await utils.answer(message, "Нет данных")
            return

        logs = self.db[user_id]
        report = f"⚠️ REPORT\n\nUser: {args}\nID: {user_id}\n\n"

        for log in logs[-5:]:
            link = f"https://t.me/c/{str(log['chat'])[4:]}/{log['msg_id']}"
            report += f"• {log['text']}\n{link}\n\n"

        await utils.answer(message, report)

    async def scamlogcmd(self, message):
        text = "📊 Scam log:\n\n"

        for uid, logs in self.db.items():
            text += f"{uid}: {len(logs)} сообщений\n"

        await utils.answer(message, text)

    async def clearscamcmd(self, message):
        self.db = {}
        await utils.answer(message, "Лог очищен")
