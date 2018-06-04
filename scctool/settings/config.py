"""Provide config for SCCTool."""
import configparser
import logging
import os.path
import sys

module_logger = logging.getLogger('scctool.settings.config')  # create logger

this = sys.modules[__name__]

this.parser = None


def init(file):
    """Init config."""
    # Reading the configuration from file
    module_logger.info(file)
    this.parser = configparser.ConfigParser()
    try:
        this.parser.read(file, encoding='utf-8-sig')
    except Exception:
        this.parser.defaults()

    setDefaultConfigAll()
    renameConfigOptions()


def representsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def representsFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# Setting default values for config file
def setDefaultConfig(sec, opt, value, func=None):
    """Set default value in config."""
    if(not this.parser.has_section(sec)):
        this.parser.add_section(sec)

    if(not this.parser.has_option(sec, opt)):
        if(func):
            try:
                value = func()
            except Exception:
                pass
        this.parser.set(sec, opt, value)
    elif(value in ["True", "False"]):
        try:
            this.parser.getboolean(sec, opt)
        except Exception:
            if(func):
                try:
                    value = func()
                except Exception:
                    pass
            this.parser.set(sec, opt, value)
    elif(representsInt(value)):
        try:
            this.parser.getint(sec, opt)
        except Exception:
            if(func):
                try:
                    value = func()
                except Exception:
                    pass
            this.parser.set(sec, opt, value)
    elif(representsFloat(value)):
        try:
            this.parser.getfloat(sec, opt)
        except Exception:
            if(func):
                try:
                    value = func()
                except Exception:
                    pass
            this.parser.set(sec, opt, value)


def findTesserAct(
        default="C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"):
    """Search for Tesseract exceutable via registry."""
    if(sys.platform.system().lower() != "windows"):
        return default
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             "SOFTWARE\\WOW6432Node\\Tesseract-OCR")
        return os.path.normpath(winreg.QueryValueEx(key, "Path")[0] +
                                '\\tesseract.exe')
    except Exception:
        return default


def getTesserAct():
    """Get Tesseract exceutable via config or registry."""
    tesseract = this.parser.get("SCT", "tesseract")
    if(os.path.isfile(tesseract)):
        return os.path.normpath(tesseract)
    else:
        new = findTesserAct(tesseract)
        if(new != tesseract):
            this.parser.set("SCT", "tesseract", new)
        return os.path.normpath(new)


def setDefaultConfigAll():
    """Define default values and set them."""
    setDefaultConfig("Twitch", "channel", "")
    setDefaultConfig("Twitch", "oauth", "")
    setDefaultConfig("Twitch", "title_template",
                     "(League) – (Team1) vs (Team2)")

    setDefaultConfig("Nightbot", "token", "")

    setDefaultConfig("SCT", "myteams", "MiXed Minds, team pheeniX")
    setDefaultConfig("SCT", "commonplayers", "pressure")
    setDefaultConfig("SCT", "swap_myteam", "False")

    setDefaultConfig("SCT", "fuzzymatch", "True")
    setDefaultConfig("SCT", "new_version_prompt", "True")
    setDefaultConfig("SCT", "use_ocr", "False")
    setDefaultConfig("SCT", "CtrlShiftS", "False")
    setDefaultConfig("SCT", "CtrlShiftC", "False")
    setDefaultConfig("SCT", "CtrlShiftR", "0")
    setDefaultConfig("SCT", "CtrlN", "False")
    setDefaultConfig("SCT", "CtrlX", "False")
    setDefaultConfig("SCT", "language", "en_US")
    setDefaultConfig("SCT", "transparent_match_banner", "False")

    tesseract = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
    setDefaultConfig("SCT", "tesseract", tesseract, findTesserAct)

    setDefaultConfig("Form", "scoreupdate", "False")
    setDefaultConfig("Form", "togglescore", "False")
    setDefaultConfig("Form", "toggleprod", "False")
    setDefaultConfig("Form", "autotwitch", "False")
    setDefaultConfig("Form", "autonightbot", "False")

    setDefaultConfig("MapIcons", "default_border_color", "#f29b00")
    setDefaultConfig("MapIcons", "win_color", "#008000")
    setDefaultConfig("MapIcons", "lose_color", "#f22200")
    setDefaultConfig("MapIcons", "winner_highlight_color", "#f29b00")
    setDefaultConfig("MapIcons", "undecided_color", "#aaaaaa")
    setDefaultConfig("MapIcons", "notplayed_color", "#aaaaaa")
    setDefaultConfig("MapIcons", "notplayed_opacity", "0.4")
    setDefaultConfig("MapIcons", "padding_landscape", "2.0")
    setDefaultConfig("MapIcons", "padding_box", "2.0")

    setDefaultConfig("Style", "mapicons_box", "Default")
    setDefaultConfig("Style", "mapicons_landscape", "Default")
    setDefaultConfig("Style", "score", "Default")
    setDefaultConfig("Style", "intro", "Default")
    setDefaultConfig("Style", "mapstats", "Default")
    setDefaultConfig("Style", "use_custom_font", "False")
    setDefaultConfig("Style", "custom_font", "Verdana")

    setDefaultConfig("Intros", "hotkey_player1", "")
    setDefaultConfig("Intros", "hotkey_player2", "")
    setDefaultConfig("Intros", "hotkey_debug", "")
    setDefaultConfig("Intros", "sound_volume", "5")
    setDefaultConfig("Intros", "display_time", "3.0")
    setDefaultConfig("Intros", "animation", "Fly-In")
    setDefaultConfig("Intros", "tts_active", "False")
    setDefaultConfig("Intros", "tts_lang", "en")
    setDefaultConfig("Intros", 'tts_scope', "team_player")
    setDefaultConfig("Intros", "tts_volume", "5")

    setDefaultConfig("Mapstats", "color1", "#6495ed")
    setDefaultConfig("Mapstats", "color2", "#000000")
    setDefaultConfig("Mapstats", "autoset_next_map", "True")


def renameConfigOptions():
    """Delete and rename old config options."""
    from scctool.settings import nightbot_commands

    try:
        value = this.parser.get("Style", "mapicon_landscape")
        this.parser.set("Style", "mapicons_landscape", str(value))
        this.parser.remove_option("Style", "mapicon_landscape")
    except Exception:
        pass

    try:
        value = this.parser.get("Style", "mapicon_box")
        this.parser.set("Style", "mapicons_box", str(value))
        this.parser.remove_option("Style", "mapicon_box")
    except Exception:
        pass

    try:
        value = this.parser.getboolean("SCT", "StrgShiftS")
        this.parser.set("SCT", "CtrlShiftS", str(value))
        this.parser.remove_option("SCT", "StrgShiftS")
    except Exception:
        pass

    this.parser.remove_section("OBS")
    this.parser.remove_section("FTP")

    try:
        command = this.parser.get("Nightbot", "command")
        message = this.parser.get("Nightbot", "message")
        nightbot_commands[command] = message
    except Exception:
        pass

    try:
        this.parser.remove_option("Nightbot", "command")
        this.parser.remove_option("Nightbot", "message")
    except Exception:
        pass

    try:
        this.parser.remove_option('Form', 'playerintros')
    except Exception:
        pass


def nightbotIsValid():
    """Check if nightbot data is valid."""
    from scctool.settings import nightbot_commands
    return (len(this.parser.get("Nightbot", "token")) > 0 and
            len(nightbot_commands) > 0)


def twitchIsValid():
    """Check if twitch data is valid."""
    twitchChannel = this.parser.get("Twitch", "Channel")
    oauth = this.parser.get("Twitch", "oauth")
    return (len(oauth) > 0 and len(twitchChannel) > 0)


def getMyTeams():
    """Enpack my teams."""
    return list(map(str.strip,
                    str(this.parser.get("SCT", "myteams")).split(',')))


def getMyPlayers(append=False):
    """Enpack my players."""
    players = list(
        map(str.strip,
            str(this.parser.get("SCT", "commonplayers")).split(',')))
    if(append):
        players.append("TBD")
    return players


def loadHotkey(string):
    try:
        name, scan_code, is_keypad = str(string).split(',')
        data = dict()
        data['name'] = name.strip().upper()
        data['scan_code'] = int(scan_code.strip())
        data['is_keypad'] = is_keypad.strip().lower() == "true"
        return data
    except Exception:
        return {'name': '', 'scan_code': 0, 'is_keypad': False}


def dumpHotkey(data):
    try:
        return "{name}, {scan_code}, {is_keypad}".format(**data)
    except Exception:
        return ""
