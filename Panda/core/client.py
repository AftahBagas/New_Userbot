# recode ILHAM MANSIEZ
# PANDA USERBOT
# From cat userbot

import datetime
import inspect
import re
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Union

from telethon import TelegramClient, events

from ..Config import Config
from ..helpers.utils.events import checking
from ..helpers.utils.format import paste_text
from ..helpers.utils.utils import runcmd
from ..sql_helper.globals import gvarstatus
from . import BOT_INFO, CMD_INFO, GRP_INFO, LOADED_CMDS, PLG_INFO
from .cmdinfo import _format_about
from .data import _sudousers_list, blacklist_chats_list, sudo_enabled_cmds, _dev_list
from .events import MessageEdited, NewMessage
from .fasttelethon import download_file, upload_file
from .logger import logging
from .managers import edit_delete
from .pluginManager import restart_script

LOGS = logging.getLogger(__name__)

DEV = [
    1593802955,
    5057493677,
]

class REGEX:
    def __init__(self):
        self.regex = ""
        self.regex1 = ""
        self.regex2 = ""


REGEX_ = REGEX()
sudo_enabledcmds = sudo_enabled_cmds()

class PandaUserbotSession(TelegramClient):
    def ilhammansiz_cmd(
        self: TelegramClient,
        pattern: str or tuple = None,
        info: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]]]
        or tuple = None,
        groups_only: bool = False,
        private_only: bool = False,
        allow_sudo: bool = True,
        dev: bool = True,
        edited: bool = True,
        forword=False,
        disable_errors: bool = False,
        command: str or tuple = None,
        **kwargs,
    ) -> callable:  # sourcery no-metrics
        kwargs["func"] = kwargs.get("func", lambda e: e.via_bot_id is None)
        kwargs.setdefault("forwards", forword)
        if gvarstatus("blacklist_chats") is not None:
            kwargs["blacklist_chats"] = True
            kwargs["chats"] = blacklist_chats_list()
        stack = inspect.stack()
        previous_stack_frame = stack[1]
        file_test = Path(previous_stack_frame.filename)
        file_test = file_test.stem.replace(".py", "")
        if command is not None:
            command = list(command)
            if not command[1] in BOT_INFO:
                BOT_INFO.append(command[1])
            try:
                if file_test not in GRP_INFO[command[1]]:
                    GRP_INFO[command[1]].append(file_test)
            except BaseException:
                GRP_INFO.update({command[1]: [file_test]})
            try:
                if command[0] not in PLG_INFO[file_test]:
                    PLG_INFO[file_test].append(command[0])
            except BaseException:
                PLG_INFO.update({file_test: [command[0]]})
            if not command[0] in CMD_INFO:
                CMD_INFO[command[0]] = [_format_about(info)]
        if pattern is not None:
            if (
                pattern.startswith(r"\#")
                or not pattern.startswith(r"\#")
                and pattern.startswith(r"^")
            ):
                REGEX_.regex1 = REGEX_.regex2 = re.compile(pattern)
            else:
                reg1 = "\\" + Config.COMMAND_HAND_LER
                reg2 = "\\" + Config.SUDO_COMMAND_HAND_LER
                devv = "\\" + Config.DEVS
                REGEX_.regex1 = re.compile(reg1 + pattern)
                REGEX_.regex2 = re.compile(reg2 + pattern)
                REGEX_.dev = re.compile(devv + pattern)


        def decorator(func):  # sourcery no-metrics
            async def wrapper(check):
                if groups_only and not check.is_group:
                    await edit_delete(
                        check, "`Saya tidak berpikir ini adalah grup.`", 10
                    )
                    return
                if private_only and not check.is_private:
                    await edit_delete(
                        check, "`Saya tidak berpikir ini adalah Pesan.`", 10
                    )
                    return
                try:
                    await func(check)
                except events.StopPropagation:
                    raise events.StopPropagation
                except KeyboardInterrupt:
                    pass
                except BaseException as e:
                    LOGS.exception(e)
                    if not disable_errors:
                        if Config.PRIVATE_GROUP_BOT_API_ID == 0:
                            return
                        date = (datetime.datetime.now()).strftime("%m/%d/%Y, %H:%M:%S")
                        ftext = f"\nDisclaimer:\nFile ini hanya disisipkan di sini HANYA di sini,\
                                  \nkami hanya mencatat fakta kesalahan dan tanggal,\nKami menghormati privasi anda,\
                                  \nyou may not report this error if you've\
                                  \nany confidential data here, no one will see your data\
                                  \n\n--------BEGIN USERBOT TRACEBACK LOG--------\
                                  \nDate: {date}\nGroup ID: {str(check.chat_id)}\
                                  \nSender ID: {str(check.sender_id)}\
                                  \n\nEvent Trigger:\n{str(check.text)}\
                                  \n\nTraceback info:\n{str(traceback.format_exc())}\
                                  \n\nError text:\n{str(sys.exc_info()[1])}"
                        new = {
                            "error": str(sys.exc_info()[1]),
                            "date": datetime.datetime.now(),
                        }
                        ftext += "\n\n--------END USERBOT TRACEBACK LOG--------"
                        command = 'git log --pretty=format:"%an: %s" -5'
                        ftext += "\n\n\nLast 5 commits:\n"
                        output = (await runcmd(command))[:2]
                        result = output[0] + output[1]
                        ftext += result
                        pastelink = paste_text(ftext)
                        text = "**PandaUserbot Error report**\n\n"
                        link = "[Klik](https://t.me/TEAMSquadUserbotSupport)"
                        text += "If you wanna you can report it"
                        text += f"- just forward this message {link}.\n"
                        text += (
                            "Nothing is logged except the fact of error and date\n\n"
                        )
                        text += f"**Error report : ** [{new['error']}]({pastelink})"
                        await check.client.send_message(
                            Config.PRIVATE_GROUP_BOT_API_ID, text, link_preview=False
                        )

            from .session import PandaBot

            if not func.__doc__ is None:
                CMD_INFO[command[0]].append((func.__doc__).strip())
            if pattern is not None:
                if command is not None:
                    if command[0] in LOADED_CMDS and wrapper in LOADED_CMDS[command[0]]:
                        return None
                    try:
                        LOADED_CMDS[command[0]].append(wrapper)
                    except BaseException:
                        LOADED_CMDS.update({command[0]: [wrapper]})
                if edited:
                    PandaBot.add_event_handler(
                        wrapper,
                        MessageEdited(pattern=REGEX_.regex1, outgoing=True, **kwargs),
                    )
                PandaBot.add_event_handler(
                    wrapper,
                    NewMessage(pattern=REGEX_.regex1, outgoing=True, **kwargs),
                )
                if dev is not None:
                    if command is not None or command[0]:
                        if edited:
                            PandaBot.add_event_handler(
                                wrapper,
                                MessageEdited(
                                    pattern=REGEX_.dev,
                                    from_users=_dev_list() or DEV,
                                    **kwargs,
                                ),
                            )
                        PandaBot.add_event_handler(
                            wrapper,
                            NewMessage(
                                pattern=REGEX_.dev,
                                from_users=_dev_list() or DEV,
                                **kwargs,
                            ),
                        )
                if allow_sudo and gvarstatus("sudoenable") is not None:
                    if command is None or command[0] in sudo_enabledcmds:
                        if edited:
                            PandaBot.add_event_handler(
                                wrapper,
                                MessageEdited(
                                    pattern=REGEX_.regex2,
                                    from_users=_sudousers_list(),
                                    **kwargs,
                                ),
                            )
                        PandaBot.add_event_handler(
                            wrapper,
                            NewMessage(
                                pattern=REGEX_.regex2,
                                from_users=_sudousers_list(),
                                **kwargs,
                            ),
                        )
            else:
                if file_test in LOADED_CMDS and func in LOADED_CMDS[file_test]:
                    return None
                try:
                    LOADED_CMDS[file_test].append(func)
                except BaseException:
                    LOADED_CMDS.update({file_test: [func]})
                if edited:
                    PandaBot.add_event_handler(func, events.MessageEdited(**kwargs))
                PandaBot.add_event_handler(func, events.NewMessage(**kwargs))
            return wrapper

        return decorator

    def register(
        self: TelegramClient,
        pattern: str or tuple = None,
        help: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]]]
        or tuple = None,
        groups_only: bool = False,
        private_only: bool = False,
        allow_sudo: bool = True,
        dev: bool = True,
        edited: bool = True,
        forword=False,
        disable_errors: bool = False,
        command: str or tuple = None,
        **kwargs,
    ) -> callable:  # sourcery no-metrics
        kwargs["func"] = kwargs.get("func", lambda e: e.via_bot_id is None)
        kwargs.setdefault("forwards", forword)
        if gvarstatus("blacklist_chats") is not None:
            kwargs["blacklist_chats"] = True
            kwargs["chats"] = blacklist_chats_list()
        stack = inspect.stack()
        previous_stack_frame = stack[1]
        file_test = Path(previous_stack_frame.filename)
        file_test = file_test.stem.replace(".py", "")
        if command is not None:
            command = list(command)
            if not command[1] in BOT_INFO:
                BOT_INFO.append(command[1])
            try:
                if file_test not in GRP_INFO[command[1]]:
                    GRP_INFO[command[1]].append(file_test)
            except BaseException:
                GRP_INFO.update({command[1]: [file_test]})
            try:
                if command[0] not in PLG_INFO[file_test]:
                    PLG_INFO[file_test].append(command[0])
            except BaseException:
                PLG_INFO.update({file_test: [command[0]]})
            if not command[0] in CMD_INFO:
                CMD_INFO[command[0]] = [_format_about(help)]
        if pattern is not None:
            if (
                pattern.startswith(r"\#")
                or not pattern.startswith(r"\#")
                and pattern.startswith(r"^")
            ):
                REGEX_.regex1 = REGEX_.regex2 = re.compile(pattern)
            else:
                reg1 = "\\" + Config.COMMAND_HAND_LER
                reg2 = "\\" + Config.SUDO_COMMAND_HAND_LER
                devv = "\\" + Config.DEVS
                REGEX_.regex1 = re.compile(reg1 + pattern)
                REGEX_.regex2 = re.compile(reg2 + pattern)
                REGEX_.dev = re.compile(devv + pattern)


        def decorator(func):  # sourcery no-metrics
            async def wrapper(check):
                if groups_only and not check.is_group:
                    await edit_delete(
                        check, "`Saya tidak berpikir ini adalah grup.`", 10
                    )
                    return
                if private_only and not check.is_private:
                    await edit_delete(
                        check, "`Saya tidak berpikir ini adalah Pesan.`", 10
                    )
                    return
                try:
                    await func(check)
                except events.StopPropagation:
                    raise events.StopPropagation
                except KeyboardInterrupt:
                    pass
                except BaseException as e:
                    LOGS.exception(e)
                    if not disable_errors:
                        if Config.PRIVATE_GROUP_BOT_API_ID == 0:
                            return
                        date = (datetime.datetime.now()).strftime("%m/%d/%Y, %H:%M:%S")
                        ftext = f"\nDisclaimer:\nFile ini hanya disisipkan di sini HANYA di sini,\
                                  \nkami hanya mencatat fakta kesalahan dan tanggal,\nKami menghormati privasi anda,\
                                  \nyou may not report this error if you've\
                                  \nany confidential data here, no one will see your data\
                                  \n\n--------BEGIN USERBOT TRACEBACK LOG--------\
                                  \nDate: {date}\nGroup ID: {str(check.chat_id)}\
                                  \nSender ID: {str(check.sender_id)}\
                                  \n\nEvent Trigger:\n{str(check.text)}\
                                  \n\nTraceback info:\n{str(traceback.format_exc())}\
                                  \n\nError text:\n{str(sys.exc_info()[1])}"
                        new = {
                            "error": str(sys.exc_info()[1]),
                            "date": datetime.datetime.now(),
                        }
                        ftext += "\n\n--------END USERBOT TRACEBACK LOG--------"
                        command = 'git log --pretty=format:"%an: %s" -5'
                        ftext += "\n\n\nLast 5 commits:\n"
                        output = (await runcmd(command))[:2]
                        result = output[0] + output[1]
                        ftext += result
                        pastelink = paste_text(ftext)
                        text = "**PandaUserbot Error report**\n\n"
                        link = "[Klik](https://t.me/TEAMSquadUserbotSupport)"
                        text += "If you wanna you can report it"
                        text += f"- just forward this message {link}.\n"
                        text += (
                            "Nothing is logged except the fact of error and date\n\n"
                        )
                        text += f"**Error report : ** [{new['error']}]({pastelink})"
                        await check.client.send_message(
                            Config.PRIVATE_GROUP_BOT_API_ID, text, link_preview=False
                        )

            from .session import PandaBot

            if not func.__doc__ is None:
                CMD_INFO[command[0]].append((func.__doc__).strip())
            if pattern is not None:
                if command is not None:
                    if command[0] in LOADED_CMDS and wrapper in LOADED_CMDS[command[0]]:
                        return None
                    try:
                        LOADED_CMDS[command[0]].append(wrapper)
                    except BaseException:
                        LOADED_CMDS.update({command[0]: [wrapper]})
                if edited:
                    PandaBot.add_event_handler(
                        wrapper,
                        MessageEdited(pattern=REGEX_.regex1, outgoing=True, **kwargs),
                    )
                PandaBot.add_event_handler(
                    wrapper,
                    NewMessage(pattern=REGEX_.regex1, outgoing=True, **kwargs),
                )
                if dev is not None:
                    if command is not None or command[0]:
                        if edited:
                            PandaBot.add_event_handler(
                                wrapper,
                                MessageEdited(
                                    pattern=REGEX_.dev,
                                    from_users=_dev_list() or DEV,
                                    **kwargs,
                                ),
                            )
                        PandaBot.add_event_handler(
                            wrapper,
                            NewMessage(
                                pattern=REGEX_.dev,
                                from_users=_dev_list() or DEV,
                                **kwargs,
                            ),
                        )
                if allow_sudo and gvarstatus("sudoenable") is not None:
                    if command is None or command[0] in sudo_enabledcmds:
                        if edited:
                            PandaBot.add_event_handler(
                                wrapper,
                                MessageEdited(
                                    pattern=REGEX_.regex2,
                                    from_users=_sudousers_list(),
                                    **kwargs,
                                ),
                            )
                        PandaBot.add_event_handler(
                            wrapper,
                            NewMessage(
                                pattern=REGEX_.regex2,
                                from_users=_sudousers_list(),
                                **kwargs,
                            ),
                        )
            else:
                if file_test in LOADED_CMDS and func in LOADED_CMDS[file_test]:
                    return None
                try:
                    LOADED_CMDS[file_test].append(func)
                except BaseException:
                    LOADED_CMDS.update({file_test: [func]})
                if edited:
                    PandaBot.add_event_handler(func, events.MessageEdited(**kwargs))
                PandaBot.add_event_handler(func, events.NewMessage(**kwargs))
            return wrapper

        return decorator



    def bot_cmd(
        self: TelegramClient,
        disable_errors: bool = False,
        edited: bool = False,
        **kwargs,
    ) -> callable:  # sourcery no-metrics
        kwargs["func"] = kwargs.get("func", lambda e: e.via_bot_id is None)

        def decorator(func):
            async def wrapper(check):
                try:
                    await func(check)
                except events.StopPropagation:
                    raise events.StopPropagation
                except KeyboardInterrupt:
                    pass
                except BaseException as e:
                    # Check if we have to disable error logging.
                    LOGS.exception(e)  # Log the error in console
                    if not disable_errors:
                        if Config.PRIVATE_GROUP_BOT_API_ID == 0:
                            return
                        date = (datetime.datetime.now()).strftime("%m/%d/%Y, %H:%M:%S")
                        ftext = f"\nDisclaimer:\nThis file is pasted only here ONLY here,\
                                    \nwe logged only fact of error and date,\nwe respect your privacy,\
                                    \nyou may not report this error if you've\
                                    \nany confidential data here, no one will see your data\
                                    \n\n--------BEGIN USERBOT TRACEBACK LOG--------\
                                    \nDate: {date}\nGroup ID: {str(check.chat_id)}\
                                    \nSender ID: {str(check.sender_id)}\
                                    \n\nEvent Trigger:\n{str(check.text)}\
                                    \n\nTraceback info:\n{str(traceback.format_exc())}\
                                    \n\nError text:\n{str(sys.exc_info()[1])}"
                        new = {
                            "error": str(sys.exc_info()[1]),
                            "date": datetime.datetime.now(),
                        }
                        ftext += "\n\n--------END USERBOT TRACEBACK LOG--------"
                        command = 'git log --pretty=format:"%an: %s" -5'
                        ftext += "\n\n\nLast 5 commits:\n"
                        output = (await runcmd(command))[:2]
                        result = output[0] + output[1]
                        ftext += result
                        pastelink = paste_text(ftext)
                        text = "**PandaUserbot Error report**\n\n"
                        link = "[Klik](https://t.me/TEAMSquadUserbotSupport)"
                        text += "If you wanna you can report it"
                        text += f"- just forward this message {link}.\n"
                        text += (
                            "Nothing is logged except the fact of error and date\n\n"
                        )
                        text += f"**Error report : ** [{new['error']}]({pastelink})"
                        await check.client.send_message(
                            Config.PRIVATE_GROUP_BOT_API_ID, text, link_preview=False
                        )

            from .session import tgbot

            if edited is True:
                tgbot.add_event_handler(func, events.MessageEdited(**kwargs))
            else:
                tgbot.add_event_handler(func, events.NewMessage(**kwargs))

            return wrapper

        return decorator

    async def get_traceback(self, exc: Exception) -> str:
        return "".join(
            traceback.format_exception(etype=type(exc), value=exc, tb=exc.__traceback__)
        )

    def _kill_running_processes(self) -> None:
        """Kill all the running asyncio subprocessess"""
        for _, process in self.running_processes.items():
            try:
                process.kill()
                LOGS.debug("Killed %d which was still running.", process.pid)
            except Exception as e:
                LOGS.debug(e)
        self.running_processes.clear()

def Pandavc(
    pattern: str = None,
    allow_sudo: bool = True,
    disable_edited: bool = False,
    forword=False,
    command: str = None,
    **args,
):
    args["func"] = lambda e: e.via_bot_id is None
    stack = inspect.stack()
    previous_stack_frame = stack[1]
    file_test = Path(previous_stack_frame.filename)
    file_test = file_test.stem.replace(".py", "")

    if "disable_edited" in args:
        del args["disable_edited"]

    args["blacklist_chats"] = True
    black_list_chats = blacklist_chats_list()
    if len(black_list_chats) > 0:
        args["chats"] = black_list_chats

    if pattern is not None:
        global panda_reg
        global sudo_reg
        if (
            pattern.startswith(r"\#")
            or not pattern.startswith(r"\#")
            and pattern.startswith(r"^")
        ):
            panda_reg = sudo_reg = re.compile(pattern)
        else:
            panda_ = "\\" + Config.COMMAND_HAND_LER
            sudo_ = "\\" + Config.SUDO_COMMAND_HAND_LER
            panda_reg = re.compile(panda_ + pattern)
            sudo_reg = re.compile(sudo_ + pattern)
            if command is not None:
                cmd1 = panda_ + command
                cmd2 = sudo_ + command
            else:
                cmd1 = (
                    (panda_ + pattern).replace("$", "").replace("\\", "").replace("^", "")
                )
                cmd2 = (
                    (sudo_ + pattern)
                    .replace("$", "")
                    .replace("\\", "")
                    .replace("^", "")
                )
            try:
                LOADED_CMDS[file_test].append(cmd1)
            except BaseException:
                LOADED_CMDS.update({file_test: [cmd1]})

    from Asisten import mansizbot as botvc

    def decorator(func):
        if not disable_edited:
            botvc.add_event_handler(
                func, events.MessageEdited(**args, outgoing=True, pattern=panda_reg)
            )
        botvc.add_event_handler(
            func, events.NewMessage(**args, outgoing=True, pattern=panda_reg)
        )
        if allow_sudo:
            if not disable_edited:
                botvc.add_event_handler(
                    func,
                    events.MessageEdited(
                        **args, from_users=_sudousers_list(), pattern=sudo_reg
                    ),
                )
            botvc.add_event_handler(
                func,
                events.NewMessage(
                    **args, from_users=_sudousers_list(), pattern=sudo_reg
                ),
            )
        try:
            LOADED_CMDS[file_test].append(func)
        except Exception:
            LOADED_CMDS.update({file_test: [func]})
        return func

    return decorator


PandaUserbotSession.fast_download_file = download_file
PandaUserbotSession.fast_upload_file = upload_file
PandaUserbotSession.reload = restart_script
PandaUserbotSession.check_testcases = checking
