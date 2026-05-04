from .. import loader, utils
import re

@loader.tds
class AntiScamUltraMod(loader.Module):
    """AntiScam ULTRA | made by @dexonbuy"""

    strings = {"name": "AntiScamUltra"}

    def __init__(self):
        self.bad_words = [
            "invest", "crypto", "profit", "giveaway",
            "airdrop", "earn money", "btc", "usdt"
        ]
        self.link_regex = re.compile(r"(https?://|t\.me/)")

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        me = await client.get_me()
        self.me = me.id

        # дефолт настройки
        if self.db.get("AntiScam", "enabled") is None:
            self.db.set("AntiScam", "enabled", True)

        if self.db.get("AntiScam", "notify") is None:
            self.db.set("AntiScam", "notify", True)

        if self.db.get("AntiScam", "logs") is None:
            self.db.set("AntiScam", "logs", {})

        if self.db.get("AntiScam", "whitelist") is None:
            self.db.set("AntiScam", "whitelist", [])

        # сообщение при запуске
        try:
            await client.send_message(
                "me",
                "✅ AntiScam ULTRA запущен\nmade by @dexonbuy"
            )
        except:
            pass

    async def watcher(self, message):
        if not message.text:
            return

        user = await message.get_sender()

        # игнор мусора
        if not user or user.bot or user.id == self.me:
            return

        # выключено
        if not self.db.get("AntiScam", "enabled"):
            return

        # whitelist
        if user.id in self.db.get("AntiScam", "whitelist", []):
            return

        text = message.text.lower()

        suspicious = False

        if any(word in text for word in self.bad_words):
            suspicious = True

        if self.link_regex.search(text):
            suspicious = True

        if not suspicious:
            return

        logs = self.db.get("AntiScam", "logs", {})
        logs.setdefault(str(user.id), [])
        logs[str(user.id)].append(message.text)

        self.db.set("AntiScam", "logs", logs)

        # уведомление
        if self.db.get("AntiScam", "notify"):
            try:
                await self.client.send_message(
                    "me",
                    f"⚠️ Scam detected\nUser: {user.id}\n{text}\n\nmade by @dexonbuy"
                )
            except:
                pass

    # ---------- КОМАНДЫ ----------

    async def ashelpcmd(self, message):
        """— меню"""
        text = (
            "🛡 AntiScam ULTRA\n\n"
            "Команды:\n"
            ".ashelp — меню\n"
            ".asreport <id> — отчет\n"
            ".aslog — лог\n"
            ".asclear — очистить\n"
            ".aswl <id> — whitelist\n"
            ".astoggle — вкл/выкл\n"
            ".asnotify — уведомления\n\n"
            "made by @dexonbuy"
        )
        await utils.answer(message, text)

    async def asreportcmd(self, message):
        """<id> — отчет"""
        args = utils.get_args_raw(message)

        if not args:
            await utils.answer(message, "❌ Укажи ID\n\nmade by @dexonbuy")
            return

        logs = self.db.get("AntiScam", "logs", {})

        if args not in logs:
            await utils.answer(message, "❌ Нет данных\n\nmade by @dexonbuy")
            return

        text = f"⚠️ REPORT {args}\n\n"

        for msg in logs[args][-5:]:
            text += f"• {msg}\n"

        text += "\nmade by @dexonbuy"

        await utils.answer(message, text)

    async def aslogcmd(self, message):
        """— лог"""
        logs = self.db.get("AntiScam", "logs", {})

        if not logs:
            await utils.answer(message, "📊 Пусто\n\nmade by @dexonbuy")
            return

        text = "📊 Scam log:\n\n"

        for uid, msgs in logs.items():
            text += f"{uid}: {len(msgs)} сообщений\n"

        text += "\nmade by @dexonbuy"

        await utils.answer(message, text)

    async def asclearcmd(self, message):
        """— очистка"""
        self.db.set("AntiScam", "logs", {})
        await utils.answer(message, "✅ Очищено\n\nmade by @dexonbuy")

    async def aswlcmd(self, message):
        """<id> — whitelist"""
        args = utils.get_args_raw(message)

        if not args:
            await utils.answer(message, "❌ Укажи ID\n\nmade by @dexonbuy")
            return

        wl = self.db.get("AntiScam", "whitelist", [])
        uid = int(args)

        if uid not in wl:
            wl.append(uid)

        self.db.set("AntiScam", "whitelist", wl)

        await utils.answer(message, f"✅ Добавлен {uid}\n\nmade by @dexonbuy")

    async def astogglecmd(self, message):
        """— вкл/выкл"""
        val = not self.db.get("AntiScam", "enabled")
        self.db.set("AntiScam", "enabled", val)
        await utils.answer(message, f"Enabled: {val}\n\nmade by @dexonbuy")

    async def asnotifycmd(self, message):
        """— уведомления"""
        val = not self.db.get("AntiScam", "notify")
        self.db.set("AntiScam", "notify", val)
        await utils.answer(message, f"Notify: {val}\n\nmade by @dexonbuy")
