# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from builtins import str
from builtins import object
import os
import webbrowser
import sound_lib
import paths
import widgetUtils
import config
import languageHandler
import output
import application
from wxUI.dialogs import configuration
from wxUI import commonMessageDialogs
from extra.autocompletionUsers import settings
from extra.ocr import OCRSpace
from pubsub import pub
import logging
import config_utils
log = logging.getLogger("Settings")
import keys
from collections import OrderedDict
from mysc import autostart as autostart_windows

class globalSettingsController(object):
    def __init__(self):
        super(globalSettingsController, self).__init__()
        self.dialog = configuration.configurationDialog()
        self.create_config()
        self.needs_restart = False
        self.is_started = True

    def make_kmmap(self):
        res={}
        for i in os.listdir(os.path.join(paths.app_path(), 'keymaps')):
            if ".keymap" not in i:
                continue
            try:
                res[i[:-7]] =i
            except:
                log.exception("Exception while loading keymap " + i)
        return res

    def create_config(self):
        self.kmmap=self.make_kmmap()
        self.langs = languageHandler.getAvailableLanguages()
        langs = []
        [langs.append(i[1]) for i in self.langs]
        self.codes = []
        [self.codes.append(i[0]) for i in self.langs]
        id = self.codes.index(config.app["app-settings"]["language"])
        self.kmfriendlies=[]
        self.kmnames=[]
        for k,v in list(self.kmmap.items()):
            self.kmfriendlies.append(k)
            self.kmnames.append(v)
        self.kmid=self.kmnames.index(config.app['app-settings']['load_keymap'])
        self.dialog.create_general(langs,self.kmfriendlies)
        self.dialog.general.language.SetSelection(id)
        self.dialog.general.km.SetSelection(self.kmid)
        if paths.mode == "installed":
            self.dialog.set_value("general", "autostart", config.app["app-settings"]["autostart"])
        else:
            self.dialog.general.autostart.Enable(False)
        self.dialog.set_value("general", "ask_at_exit", config.app["app-settings"]["ask_at_exit"])
        self.dialog.set_value("general", "no_streaming", config.app["app-settings"]["no_streaming"])
        self.dialog.set_value("general", "play_ready_sound", config.app["app-settings"]["play_ready_sound"])
        self.dialog.set_value("general", "speak_ready_msg", config.app["app-settings"]["speak_ready_msg"])
        self.dialog.set_value("general", "handle_longtweets", config.app["app-settings"]["handle_longtweets"])
        self.dialog.set_value("general", "use_invisible_shorcuts", config.app["app-settings"]["use_invisible_keyboard_shorcuts"])
        self.dialog.set_value("general", "disable_sapi5", config.app["app-settings"]["voice_enabled"])
        self.dialog.set_value("general", "hide_gui", config.app["app-settings"]["hide_gui"])  
        self.dialog.set_value("general", "update_period", config.app["app-settings"]["update_period"])
        self.dialog.set_value("general", "check_for_updates", config.app["app-settings"]["check_for_updates"])
        self.dialog.set_value("general", "remember_mention_and_longtweet", config.app["app-settings"]["remember_mention_and_longtweet"])
        proxyTypes = [_("System default"), _("HTTP"), _("SOCKS v4"), _("SOCKS v4 with DNS support"), _("SOCKS v5"), _("SOCKS v5 with DNS support")]
        self.dialog.create_proxy(proxyTypes)
        try:
            self.dialog.proxy.type.SetSelection(config.app["proxy"]["type"])
        except:
            self.dialog.proxy.type.SetSelection(0)
        self.dialog.set_value("proxy", "server", config.app["proxy"]["server"])
        self.dialog.set_value("proxy", "port", config.app["proxy"]["port"])
        self.dialog.set_value("proxy", "user", config.app["proxy"]["user"])
        self.dialog.set_value("proxy", "password", config.app["proxy"]["password"])

        self.dialog.realize()
        self.response = self.dialog.get_response()

    def save_configuration(self):
        if self.codes[self.dialog.general.language.GetSelection()] != config.app["app-settings"]["language"]:
            config.app["app-settings"]["language"] = self.codes[self.dialog.general.language.GetSelection()]
            languageHandler.setLanguage(config.app["app-settings"]["language"])
            self.needs_restart = True
        if self.kmnames[self.dialog.general.km.GetSelection()] != config.app["app-settings"]["load_keymap"]:
            config.app["app-settings"]["load_keymap"] =self.kmnames[self.dialog.general.km.GetSelection()]
            kmFile = open(os.path.join(paths.config_path(), "keymap.keymap"), "w")
            kmFile.close()
            self.needs_restart = True
        if config.app["app-settings"]["autostart"] != self.dialog.get_value("general", "autostart") and paths.mode == "installed":
            config.app["app-settings"]["autostart"] = self.dialog.get_value("general", "autostart")
            autostart_windows.setAutoStart(application.name, enable=self.dialog.get_value("general", "autostart"))
        if config.app["app-settings"]["use_invisible_keyboard_shorcuts"] != self.dialog.get_value("general", "use_invisible_shorcuts"):
            config.app["app-settings"]["use_invisible_keyboard_shorcuts"] = self.dialog.get_value("general", "use_invisible_shorcuts")
            pub.sendMessage("invisible-shorcuts-changed", registered=self.dialog.get_value("general", "use_invisible_shorcuts"))
        if config.app["app-settings"]["no_streaming"] != self.dialog.get_value("general", "no_streaming"):
            config.app["app-settings"]["no_streaming"] = self.dialog.get_value("general", "no_streaming")
            self.needs_restart = True
        if config.app["app-settings"]["update_period"] != self.dialog.get_value("general", "update_period"):
            config.app["app-settings"]["update_period"] = self.dialog.get_value("general", "update_period")
            self.needs_restart = True
        config.app["app-settings"]["voice_enabled"] = self.dialog.get_value("general", "disable_sapi5")
        config.app["app-settings"]["hide_gui"] = self.dialog.get_value("general", "hide_gui")
        config.app["app-settings"]["ask_at_exit"] = self.dialog.get_value("general", "ask_at_exit")
        config.app["app-settings"]["handle_longtweets"] = self.dialog.get_value("general", "handle_longtweets")
        config.app["app-settings"]["play_ready_sound"] = self.dialog.get_value("general", "play_ready_sound")
        config.app["app-settings"]["speak_ready_msg"] = self.dialog.get_value("general", "speak_ready_msg")
        config.app["app-settings"]["check_for_updates"] = self.dialog.get_value("general", "check_for_updates")
        config.app["app-settings"]["remember_mention_and_longtweet"] = self.dialog.get_value("general", "remember_mention_and_longtweet")
        if config.app["proxy"]["type"]!=self.dialog.get_value("proxy", "type") or config.app["proxy"]["server"] != self.dialog.get_value("proxy", "server") or config.app["proxy"]["port"] != self.dialog.get_value("proxy", "port") or config.app["proxy"]["user"] != self.dialog.get_value("proxy", "user") or config.app["proxy"]["password"] != self.dialog.get_value("proxy", "password"):
            if self.is_started == True:
                self.needs_restart = True
            config.app["proxy"]["type"] = self.dialog.proxy.type.Selection
            config.app["proxy"]["server"] = self.dialog.get_value("proxy", "server")
            config.app["proxy"]["port"] = self.dialog.get_value("proxy", "port")
            config.app["proxy"]["user"] = self.dialog.get_value("proxy", "user")
            config.app["proxy"]["password"] = self.dialog.get_value("proxy", "password")
        config.app.write()

class accountSettingsController(globalSettingsController):
    def __init__(self, buffer, window):
        self.user = buffer.session.db["user_name"]
        self.buffer = buffer
        self.window = window
        self.config = buffer.session.settings
        super(accountSettingsController, self).__init__()

    def create_config(self):
        self.dialog.create_general_account()
        widgetUtils.connect_event(self.dialog.general.au, widgetUtils.BUTTON_PRESSED, self.manage_autocomplete)
        self.dialog.set_value("general", "relative_time", self.config["general"]["relative_times"])
        self.dialog.set_value("general", "show_screen_names", self.config["general"]["show_screen_names"])
        self.dialog.set_value("general", "itemsPerApiCall", self.config["general"]["max_tweets_per_call"])
        self.dialog.set_value("general", "reverse_timelines", self.config["general"]["reverse_timelines"])
        rt = self.config["general"]["retweet_mode"]
        if rt == "ask":
            self.dialog.set_value("general", "retweet_mode", _(u"Ask"))
        elif rt == "direct":
            self.dialog.set_value("general", "retweet_mode", _(u"Retweet without comments"))
        else:
            self.dialog.set_value("general", "retweet_mode", _(u"Retweet with comments"))
        self.dialog.set_value("general", "persist_size", str(self.config["general"]["persist_size"]))
        self.dialog.create_reporting()
        self.dialog.set_value("reporting", "speech_reporting", self.config["reporting"]["speech_reporting"])
        self.dialog.set_value("reporting", "braille_reporting", self.config["reporting"]["braille_reporting"])
        self.dialog.create_other_buffers()
        buffer_values = self.get_buffers_list()
        self.dialog.buffers.insert_buffers(buffer_values)
        self.dialog.buffers.connect_hook_func(self.toggle_buffer_active)
        widgetUtils.connect_event(self.dialog.buffers.toggle_state, widgetUtils.BUTTON_PRESSED, self.toggle_state)
        widgetUtils.connect_event(self.dialog.buffers.up, widgetUtils.BUTTON_PRESSED, self.dialog.buffers.move_up)
        widgetUtils.connect_event(self.dialog.buffers.down, widgetUtils.BUTTON_PRESSED, self.dialog.buffers.move_down)


        self.dialog.create_ignored_clients(self.config["twitter"]["ignored_clients"])
        widgetUtils.connect_event(self.dialog.ignored_clients.add, widgetUtils.BUTTON_PRESSED, self.add_ignored_client)
        widgetUtils.connect_event(self.dialog.ignored_clients.remove, widgetUtils.BUTTON_PRESSED, self.remove_ignored_client)
        self.input_devices = sound_lib.input.Input.get_device_names()
        self.output_devices = sound_lib.output.Output.get_device_names()
        self.soundpacks = []
        [self.soundpacks.append(i) for i in os.listdir(paths.sound_path()) if os.path.isdir(os.path.join(paths.sound_path(), i)) == True ]
        self.dialog.create_sound(self.input_devices, self.output_devices, self.soundpacks)
        self.dialog.set_value("sound", "volumeCtrl", self.config["sound"]["volume"]*100)
        self.dialog.set_value("sound", "input", self.config["sound"]["input_device"])
        self.dialog.set_value("sound", "output", self.config["sound"]["output_device"])
        self.dialog.set_value("sound", "session_mute", self.config["sound"]["session_mute"])
        self.dialog.set_value("sound", "soundpack", self.config["sound"]["current_soundpack"])
        self.dialog.set_value("sound", "indicate_audio", self.config["sound"]["indicate_audio"])
        self.dialog.set_value("sound", "indicate_geo", self.config["sound"]["indicate_geo"])
        self.dialog.set_value("sound", "indicate_img", self.config["sound"]["indicate_img"])
        self.dialog.create_extras(OCRSpace.translatable_langs)
        self.dialog.set_value("extras", "sndup_apiKey", self.config["sound"]["sndup_api_key"])
        language_index = OCRSpace.OcrLangs.index(self.config["mysc"]["ocr_language"])
        self.dialog.extras.ocr_lang.SetSelection(language_index)
        self.dialog.realize()
        self.dialog.set_title(_(u"Account settings for %s") % (self.user,))
        self.response = self.dialog.get_response()

    def save_configuration(self):
        if self.config["general"]["relative_times"] != self.dialog.get_value("general", "relative_time"):
            self.needs_restart = True
            self.config["general"]["relative_times"] = self.dialog.get_value("general", "relative_time")
        self.config["general"]["show_screen_names"] = self.dialog.get_value("general", "show_screen_names")
        self.config["general"]["max_tweets_per_call"] = self.dialog.get_value("general", "itemsPerApiCall")
        if self.config["general"]["persist_size"] != self.dialog.get_value("general", "persist_size"):
            if self.dialog.get_value("general", "persist_size") == '':
                self.config["general"]["persist_size"] =-1
            else:
                try:
                    self.config["general"]["persist_size"] = int(self.dialog.get_value("general", "persist_size"))
                except ValueError:
                    output.speak("Invalid cache size, setting to default.",True)
                    self.config["general"]["persist_size"] =1764

        if self.config["general"]["reverse_timelines"] != self.dialog.get_value("general", "reverse_timelines"):
            self.needs_restart = True
            self.config["general"]["reverse_timelines"] = self.dialog.get_value("general", "reverse_timelines")
        rt = self.dialog.get_value("general", "retweet_mode")
        if rt == _(u"Ask"):
            self.config["general"]["retweet_mode"] = "ask"
        elif rt == _(u"Retweet without comments"):
            self.config["general"]["retweet_mode"] = "direct"
        else:
            self.config["general"]["retweet_mode"] = "comment"
        buffers_list = self.dialog.buffers.get_list()
        if buffers_list != self.config["general"]["buffer_order"]:
            self.needs_restart = True
            self.config["general"]["buffer_order"] = buffers_list
        self.config["reporting"]["speech_reporting"] = self.dialog.get_value("reporting", "speech_reporting")
        self.config["reporting"]["braille_reporting"] = self.dialog.get_value("reporting", "braille_reporting")
        self.config["mysc"]["ocr_language"] = OCRSpace.OcrLangs[self.dialog.extras.ocr_lang.GetSelection()]
#  if self.config["other_buffers"]["show_followers"] != self.dialog.get_value("buffers", "followers"):
#   self.config["other_buffers"]["show_followers"] = self.dialog.get_value("buffers", "followers")
#   pub.sendMessage("create-new-buffer", buffer="followers", account=self.user, create=self.config["other_buffers"]["show_followers"])
#  if self.config["other_buffers"]["show_friends"] != self.dialog.get_value("buffers", "friends"):
#   self.config["other_buffers"]["show_friends"] = self.dialog.get_value("buffers", "friends")
#   pub.sendMessage("create-new-buffer", buffer="friends", account=self.user, create=self.config["other_buffers"]["show_friends"])
#  if self.config["other_buffers"]["show_favourites"] != self.dialog.get_value("buffers", "favs"):
#   self.config["other_buffers"]["show_favourites"] = self.dialog.get_value("buffers", "favs")
#   pub.sendMessage("create-new-buffer", buffer="favourites", account=self.user, create=self.config["other_buffers"]["show_favourites"])
#  if self.config["other_buffers"]["show_blocks"] != self.dialog.get_value("buffers", "blocks"):
#   self.config["other_buffers"]["show_blocks"] = self.dialog.get_value("buffers", "blocks")
#   pub.sendMessage("create-new-buffer", buffer="blocked", account=self.user, create=self.config["other_buffers"]["show_blocks"])
#  if self.config["other_buffers"]["show_muted_users"] != self.dialog.get_value("buffers", "mutes"):
#   self.config["other_buffers"]["show_muted_users"] = self.dialog.get_value("buffers", "mutes")
#   pub.sendMessage("create-new-buffer", buffer="muted", account=self.user, create=self.config["other_buffers"]["show_muted_users"])
#  if self.config["other_buffers"]["show_events"] != self.dialog.get_value("buffers", "events"):
#   self.config["other_buffers"]["show_events"] = self.dialog.get_value("buffers", "events")
#   pub.sendMessage("create-new-buffer", buffer="events", account=self.user, create=self.config["other_buffers"]["show_events"])
        if self.config["sound"]["input_device"] != self.dialog.sound.get("input"):
            self.config["sound"]["input_device"] = self.dialog.sound.get("input")
            try:
                self.buffer.session.sound.input.set_device(self.buffer.session.sound.input.find_device_by_name(self.config["sound"]["input_device"]))
            except:
                self.config["sound"]["input_device"] = "default"
        if self.config["sound"]["output_device"] != self.dialog.sound.get("output"):
            self.config["sound"]["output_device"] = self.dialog.sound.get("output")
            try:
                self.buffer.session.sound.output.set_device(self.buffer.session.sound.output.find_device_by_name(self.config["sound"]["output_device"]))
            except:
                self.config["sound"]["output_device"] = "default"
        self.config["sound"]["volume"] = self.dialog.get_value("sound", "volumeCtrl")/100.0
        self.config["sound"]["session_mute"] = self.dialog.get_value("sound", "session_mute")
        self.config["sound"]["current_soundpack"] = self.dialog.sound.get("soundpack")
        self.config["sound"]["indicate_audio"] = self.dialog.get_value("sound", "indicate_audio")
        self.config["sound"]["indicate_geo"] = self.dialog.get_value("sound", "indicate_geo")
        self.config["sound"]["indicate_img"] = self.dialog.get_value("sound", "indicate_img")
        self.config["sound"]["sndup_api_key"] = self.dialog.get_value("extras", "sndup_apiKey")
        self.buffer.session.sound.config = self.config["sound"]
        self.buffer.session.sound.check_soundpack()
        self.config.write()

    def toggle_state(self,*args,**kwargs):
        return self.dialog.buffers.change_selected_item()

    def manage_autocomplete(self, *args, **kwargs):
        configuration = settings.autocompletionSettings(self.buffer.session.settings, self.buffer, self.window)

    def add_ignored_client(self, *args, **kwargs):
        client = commonMessageDialogs.get_ignored_client()
        if client == None: return
        if client not in self.config["twitter"]["ignored_clients"]:
            self.config["twitter"]["ignored_clients"].append(client)
            self.dialog.ignored_clients.append(client)

    def remove_ignored_client(self, *args, **kwargs):
        if self.dialog.ignored_clients.get_clients() == 0: return
        id = self.dialog.ignored_clients.get_client_id()
        self.config["twitter"]["ignored_clients"].pop(id)
        self.dialog.ignored_clients.remove_(id)

    def get_buffers_list(self):
        all_buffers=OrderedDict()
        all_buffers['home']=_(u"Home")
        all_buffers['mentions']=_(u"Mentions")
        all_buffers['dm']=_(u"Direct Messages")
        all_buffers['sent_dm']=_(u"Sent direct messages")
        all_buffers['sent_tweets']=_(u"Sent tweets")
        all_buffers['favorites']=_(u"Likes")
        all_buffers['followers']=_(u"Followers")
        all_buffers['friends']=_(u"Friends")
        all_buffers['blocks']=_(u"Blocked users")
        all_buffers['muted']=_(u"Muted users")
        list_buffers = []
        hidden_buffers=[]
        all_buffers_keys = list(all_buffers.keys())
        # Check buffers shown first.
        for i in self.config["general"]["buffer_order"]:
            if i in all_buffers_keys:
                list_buffers.append((i, all_buffers[i], True))
            # This second pass will retrieve all hidden buffers.
        for i in all_buffers_keys:
            if i not in self.config["general"]["buffer_order"]:
                hidden_buffers.append((i, all_buffers[i], False))
        list_buffers.extend(hidden_buffers)
        return list_buffers

    def toggle_buffer_active(self, ev):
        change = self.dialog.buffers.get_event(ev)
        if change == True:
            self.dialog.buffers.change_selected_item()
