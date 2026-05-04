from .. import loader, utils
import re
import asyncio

@loader.tds
class AntiScamProMod(loader.Module):
    """AntiScam PRO (DB + Settings + AI) | made by @dexonbuy"""

    strings = {"name": "AntiScamPro"}

    def __init__(self):
        self.bad_words = [
            "invest", "crypto", "profit", "giveaway",
            "airdrop", "earn money", "btc", "usdt"
        ]

        self.link_regex = re.compile(r"(https?://|t\.me/)")

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

        # настройки по умолчанию
        if not self.db.get("AntiScam", "enabled"):
            self.db.set("AntiScam", "enabled", True)

        if not self.db.get("AntiScam", "notify"):
            self.db.set("AntiScam", "notify", True)

        if not self.db.get("AntiScam", "ai"):
            self.db.set("AntiScam", "ai", False)

        print("AntiScam PRO loaded | made by @dexonbuy")

    async def watcher(self, message):
        if not message.text:
            return

        if not self.db.get("AntiScam", "enabled"):
            return

        text = message.text.lower()
        suspicious = False

        if any(word in text for word in self.bad_words):
            suspicious = True

        if self.link_regex.search(text):
            suspicious = True

        # 🧠 AI анализ
        if self.db.get("AntiScam", "ai"):
            try:
                import openai
                openai.api_key = self.db.get("AntiScam", "api")

                resp = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role":"user","content":f"Это скам? Ответь да или нет: {text}"}]
                )

                if "да" in resp.choices[0].message.content.lower():
                    suspicious = True
            except:
                pass

        if not suspicious:
            return

        user = await message.get_sender()
        user_id = user.id

        logs = self.db.get("AntiScam", "logs", {})
        logs.setdefault(str(user_id), [])

        logs[str(user_id)].append(message.text)

        self.db.set("AntiScam", "logs", logs)

        # уведомление
        if self.db.get("AntiScam", "notify"):
            try:
                await self.client.send_message(
                    "me",
                    f"⚠️ Scam detected\nUser: {user_id}\n{text}\n\nmade by @dexonbuy"
                )
            except:
                pass

    async def reportcmd(self, message):
        """<user> — отчет"""
        args = utils.get_args_raw(message)

        logs = self.db.get("AntiScam", "logs", {})

        if args not in logs:
            await utils.answer(message, "❌ Нет данных\n\nmade by @dexonbuy")
            return

        text = f"⚠️ REPORT {args}\n\n"

        for msg in logs[args][-5:]:
            text += f"• {msg}\n"

        text += "\nmade by @dexonbuy"

        await utils.answer(message, text)

    async def settingscmd(self, message):
        """— настройки"""
        text = (
            "⚙️ AntiScam Settings\n\n"
            f"Enabled: {self.db.get('AntiScam','enabled')}\n"
            f"Notify: {self.db.get('AntiScam','notify')}\n"
            f"AI: {self.db.get('AntiScam','ai')}\n\n"
            ".toggle — включить/выключить\n"
            ".notify — уведомления\n"
            ".ai — включить AI\n\n"
            "made by @dexonbuy"
        )
        await utils.answer(message, text)

    async def togglecmd(self, message):
        val = not self.db.get("AntiScam", "enabled")
        self.db.set("AntiScam", "enabled", val)
        await utils.answer(message, f"Enabled: {val}\n\nmade by @dexonbuy")

    async def notifycmd(self, message):
        val = not self.db.get("AntiScam", "notify")
        self.db.set("AntiScam", "notify", val)
        await utils.answer(message, f"Notify: {val}\n\nmade by @dexonbuy")

    async def aicmd(self, message):
        val = not self.db.get("AntiScam", "ai")
        self.db.set("AntiScam", "ai", val)
        await utils.answer(message, f"AI: {val}\n\nmade by @dexonbuy")

    async def apikeycmd(self, message):
        """<key> — установить API ключ"""
        key = utils.get_args_raw(message)
        self.db.set("AntiScam", "api", key)
        await utils.answer(message, "✅ API сохранён\n\nmade by @dexonbuy")
