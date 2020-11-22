import appdaemon.plugins.hass.hassapi as hass
import re
import datetime

######
# AutoLights App
#
# Args:
#   init:
#     "helper" that indicate of "switch" or on/off, they can also turn on/off the "switch"
#
#   actions:
#     A list of entities of "switch"
#
#         example:
#           actions:
#           - 'switch.db2_1'
#           - 'switch.db3_1'
#           - 'switch.b9'
#
#   auto_ons:
#   auto_offs:
#     A list of time,
#       <HH>:<MM>:<SS>        Absolute time all be given (HH, MM and SS), start in the first position
#                             and end with a "space" or a "'". After the "space" is free text.
#                               0 <= 'HH' <= 23
#                               0 <= 'MM' <= 59
#                               0 <= 'SS' <= 59
#
#                             example:
#                               auto_offs:
#                               - '23:00:00 absolute time'
#                               - '10:00:00 time'
#                               - '0:0:0'
#
#       [+-]<HH>:<MM>:<SS>    Relative time, to sun raise/sets, must not all be given (HH, MM and SS).
#                                '+'    after sun raise/sets shall light turn on or off
#                                '-'    before sun raise/sets shall light turn on or off
#
#                             example:
#                               auto_ons:
#                               - '-00:41:15 relative the sun'
#                               - '+4:59 safafasdfadfasdfasdfasdfasdfsdf'
#                               - '+1'
#                               - '-0'
#
#   debug:
#     Start a debug if the Args is "something"
#

class AutoLights(hass.Hass):

    def initialize(self):
        self.log("AutoLights:initialize()")

        #####
        # Globals parameters
        self.g_debug = 0
        self.g_debug_print = False
        if "debug" in self.args:
            self.log("   - _ - DEBUG - _ - ")
            self.g_debug_print = True

        self.g_init = self.args["init"]
        self.g_actions = self.args["actions"]
        self.g_auto_ons = self.args["auto_ons"]
        self.g_auto_offs = self.args["auto_offs"]

        self.log(f"  init = {self.g_init}")

        self.log(f"  actions:")
        for action in self.g_actions:
            self.log(f"    - {action}")

        self.log(f"  auto_ons:")
        for auto_on in self.g_auto_ons:
            self.log(f"    - {auto_on}")
        self.log(f"  auto_offs:")
        for auto_off in self.g_auto_offs:
            self.log(f"    - {auto_off}")

        #####
        # Action
        self.log("")
        assert self.entity_exists(self.g_init), f"Illegal format: {self.g_init}"
        for action in self.g_actions:
            assert self.entity_exists(action),  f"Illegal format: {action}"

        self.log(f"  listen_state(action_cb, {self.g_init})")
        self.listen_state(self.action_cb, self.g_init)

        self.log(f"  action:")
        for action in self.g_actions:
            self.log(f"    - listen_state(manual_cb, {action})")
            self.listen_state(self.manual_cb, action)

        self.log("  auto_on:")
        for auto_on in self.g_auto_ons:
            sign, time = self.timestr_convert(auto_on)
            if sign in ['+', '-']:
                self.log(f"    - run_at_sunset(on_cb, offset={time})")
                self.run_at_sunset(self.on_cb, offset=time)
            else:
                self.log(f"    - run_daily(on_cb, offset={time})")
                self.run_daily(self.on_cb, time)

        self.log("  auto_off:")
        for auto_off in self.g_auto_offs:
            sign, time = self.timestr_convert(auto_off)
            if sign in ['+', '-']:
                self.log(f"    - run_at_sunrise(off_cb, offset={time})")
                self.run_at_sunrise(self.off_cb, offset=time)
            else:
                self.log(f"    - run_daily(off_cb, offset={time})")
                self.run_daily(self.off_cb, time)

        self.log("return()")

    def manual_cb(self, entity, attribute, old, new, kwargs):
        self.g_debug += 1
        d = self.g_debug
        self.debug(d, "AutoLights:manual_cb(")
        self.debug(d, f"    entity    = {entity}")
        self.debug(d, f"    attribute = {attribute}")
        self.debug(d, f"    old       = {old}")
        self.debug(d, f"    new       = {new}")
        self.debug(d, f"    kwargs    = {kwargs}")
        self.debug(d, ")")

        assert attribute == 'state',     f"Illegal format: {attribute}"
        assert old != new,               f"Illegal format: {old}"
        assert new in ['on', 'off'],     f"Illegal format: {new}"

        if new == "on":
            self.debug(d, f"  turn_on({self.g_init})")
            self.turn_on(self.g_init)
        else:
            self.debug(d, f"  turn_off({self.g_init})")
            self.turn_off(self.g_init)

        self.debug(d, "return()")
        self.g_debug -= 1

    def action_cb(self, entity, attribute, old, new, kwargs):
        self.g_debug += 1
        d = self.g_debug
        self.debug(d, "AutoLights:action_cb(")
        self.debug(d, f"    entity    = {entity}")
        self.debug(d, f"    attribute = {attribute}")
        self.debug(d, f"    old       = {old}")
        self.debug(d, f"    new       = {new}")
        self.debug(d, f"    kwargs    = {kwargs}")
        self.debug(d, ")")

        assert attribute == 'state',     f"Illegal format: {attribute}"
        assert old != new,               f"Illegal format: {old}"
        assert new in ['on', 'off'],     f"Illegal format: {new}"

        for lamp in self.g_actions:
            self.debug(d, f"  - {lamp}: state={new})")
            if new == "on": self.turn_on(lamp)
            else:           self.turn_off(lamp)

        self.debug(d, "return()")
        self.g_debug -= 1

    def off_cb(self, kwargs):
        self.g_debug += 1
        d = self.g_debug
        self.debug(d, "AutoLights:off_cb(")
        self.debug(d, f"    kwargs={kwargs}")
        self.debug(d, ")")

        self.debug(d, f"  turn_off({self.g_init})")
        self.turn_off(self.g_init)

        self.debug(d, "return()")
        self.g_debug -= 1

    def on_cb(self, kwargs):
        self.g_debug += 1
        d = self.g_debug
        self.debug(d, "AutoLights:on_cb(")
        self.debug(d, f"    kwargs={kwargs}")
        self.debug(d, ")")

        self.debug(d, f"  turn_on({self.g_init})")
        self.turn_on(self.g_init)

        self.debug(d, "return()")
        self.g_debug -= 1

    def timestr_convert(self, timestr):
        self.g_debug += 1
        d = self.g_debug
        self.debug(d, "AutoLights:timestr_convert(")
        self.debug(d, f"    timestr={timestr}")
        self.debug(d, "): sign, time")

        sign, hh, mm, ss = self.timestr_resolve(timestr)

        if sign in ['+', '-']:
            if hh != "0":
                if sign == "-": hh = f"{sign}{hh}"
                sign = "+"

            if mm != "0":
                if sign == "-": mm = f"{sign}{mm}"
                sign = "+"

            if sign == "-": ss = f"{sign}{ss}"

            if hh != "0":
                time = datetime.timedelta(hours=int(hh), minutes=int(mm), seconds=int(ss)).total_seconds()
                self.debug(d, f"  {time} = datetime.timedelta({hh}, {mm}, {ss}).total_seconds()")
            elif mm != "0":
                time = datetime.timedelta(minutes=int(mm), seconds=int(ss)).total_seconds()
                self.debug(d, f"  {time} = datetime.timedelta({mm}, {ss}).total_seconds()")
            else:
                time = datetime.timedelta(seconds=int(ss)).total_seconds()
                self.debug(d, f"  {time} = datetime.timedelta({ss}).total_seconds()")
        else:
            time = datetime.time(int(hh), int(mm), int(ss))
            self.debug(d, f"  {time} = datetime.time({hh}, {mm}, {ss})")

        self.debug(d, f"return(sign={sign}, time={time})")
        self.g_debug -= 1
        return sign, time

    def timestr_resolve(self, timestr):
        self.g_debug += 1
        d = self.g_debug
        self.debug(d, "AutoLights:timestr_resolve(")
        self.debug(d, f"    timestr={timestr}")
        self.debug(d, "): sign, hh, mm, ss")

        sign = ""
        hh = "0"
        mm = "0"
        ss = "0"

        assert len(timestr) != 0,             f"Illegal format: {timestr}"
        tmp = re.split(" ", timestr)[0]
        assert len(tmp) != 0,                 f"Illegal format: {timestr}"
        tmp = re.split(":", tmp)
        assert len(tmp[0]) != 0,              f"Illegal format: {timestr}"

        if tmp[0][0] in ['+', '-']:
            assert len(tmp) in [1, 2, 3],     f"Illegal format: {timestr}"
            sign = tmp[0][0]
            tmp[0] = tmp[0][1:len(tmp[0])]
        else:
            assert len(tmp) in [3],           f"Illegal format: {timestr}"

        level = len(tmp)
        for nbr in tmp:
            assert nbr.isnumeric(),           f"Illegal format: {timestr}"
            if level == 3:  # Hours
                assert int(nbr) >= 0,         f"Illegal format: {timestr}"
                assert int(nbr) < 24,         f"Illegal format: {timestr}"
                hh = f"{int(nbr)}"

            if level == 2:  # min
                assert int(nbr) >= 0,          f"Illegal format: {timestr}"
                assert int(nbr) < 60,          f"Illegal format: {timestr}"
                mm = f"{int(nbr)}"

            if level == 1:  # sec
                assert int(nbr) >= 0,          f"Illegal format: {timestr}"
                assert int(nbr) < 60,          f"Illegal format: {timestr}"
                ss = f"{int(nbr)}"
            level -= 1

        self.debug(d, f"return(sign={sign}, hh={hh}, mm={mm}, ss={ss})")
        self.g_debug -= 1
        return sign, hh, mm, ss

    def debug(self, debug_offset, debug_text):
        # debug_offset: the offset (1, 2, 3....)
        # debug_text  : the text
        if self.g_debug_print:
            offset = debug_offset * "    "
            self.log(f"{offset}{debug_text}")
