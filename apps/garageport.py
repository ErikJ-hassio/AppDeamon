import appdaemon.plugins.hass.hassapi as hass
import globals

#
# GaragePort App
#
# Args:
#   init:
#     "helper" that initiate the sequence
#
#   code:
#     the code
#
#   code_input:
#     "helper" the is placeholder for the code
#
#   action:
#     "switch" that control the physically "garageport"
#
#   timer:
#     the timer that "reset" init
#
#   power:
#     "switch" that control the power to physically "garageport"
#
#   debug:
#     Starta debug if the Args is "something"
#


class GaragePort(hass.Hass):

    def initialize(self):
        self.log("GaragePort:initialize()")

        #####
        # globals parameters
        self.g_debug = 0
        self.g_debug_print = False
        if "debug" in self.args:
            self.log("   - _ - DEBUG - _ - ")
            self.g_debug_print = True

        self.g_init = self.args["init"]
        self.g_code = self.args["code"]
        self.g_code_input = self.args["code_input"]
        self.g_action = self.args["action"]
        self.g_timer = self.args["timer"]
        self.g_power = self.args["power"]
        self.g_persons = self.args["persons"]

        self.log(f"  init       = {self.g_init}")
        self.log(f"  code       = ******")
        self.log(f"  code_input = {self.g_code_input}")
        self.log(f"  action     = {self.g_action}")
        self.log(f"  timer      = {self.g_timer}")
        self.log(f"  power      = {self.g_power}")
        self.log("  persons:")
        for person in self.g_persons:
            self.log(f"    - {person}")

        #####
        # Action
        self.log("")

        user = globals.user_ids.values()
        for person in self.g_persons:
            tmp = f"person.{person}"
            assert self.entity_exists(tmp),           f"Illegal format: {tmp}"
            assert person in user,                    f"Illegal format: {person}"
        assert self.entity_exists(self.g_init),       f"Illegal format: {self.g_init}"
        assert self.entity_exists(self.g_code_input), f"Illegal format: {self.g_code_input}"
        assert self.entity_exists(self.g_action),     f"Illegal format: {self.g_action}"
        assert self.entity_exists(self.g_power),      f"Illegal format: {self.g_power}"

        self.log(f"  listen_state(action_cb, {self.g_init}, new='on')")
        self.listen_state(self.action_cb, self.g_init, new="on")

        self.log("return()")

    def action_cb(self, entity, attribute, old, new, kwargs):
        self.g_debug += 1
        d = self.g_debug
        self.debug(d, "GaragePort:action_cb(")
        self.debug(d, f"    entity    = {entity}")
        self.debug(d, f"    attribute = {attribute}")
        self.debug(d, f"    old       = {old}")
        self.debug(d, f"    new       = {new}")
        self.debug(d, f"    kwargs    = {kwargs}")
        self.debug(d, ")")

        assert entity == self.g_init,    f"Illegal format: {entity}"
        assert attribute == 'state',     f"Illegal format: {attribute}"
        assert old != new,               f"Illegal format: {old}"
        assert new in ['on', 'off'],     f"Illegal format: {new}"

        # {'entity_id': 'input_boolean.garageport', 'state': 'on',
        #  'attributes': {'editable': True, 'friendly_name': 'Garageport'},
        #  'last_changed': '2020-11-21T14:08:33.142488+00:00', 'last_updated': '2020-11-21T14:08:33.142488+00:00',
        #  'context': {'id': 'def3224ea1bd584f3acd68b7b2e44cac', 'parent_id': None,
        #              'user_id': '991defd8cdab4044978bff2a052569e7'}}
        user_id = self.get_state(entity_id=self.g_init, attribute='all')['context']['user_id']
        user = globals.user_ids[user_id]
        self.debug(d, f"   user = {user}: {user_id}")

        if user in self.g_persons:
            self.debug(d, f"   access ({user})")
            if self.get_tracker_state(f"person.{user}") == "home":
                self.debug(d, f"   At HOME ({user})")
                if self.get_state(self.g_code_input) == self.g_code:
                    self.debug(d, f"   Valid code ({user})")
                    self.set_textvalue(self.g_code_input, "")
                    self.turn_on(self.g_action)
                    self.debug(d, f"   Garage door open!!! ({user})")
                    self.notify(f"Garageporten öppnas!!! ({user})", title="Garageport")
                else:
                    self.debug(d, f"   Faulty password ({user})")
                    self.notify(f"Felaktigt lösenord ({user})", title="Garageport")
            else:
                self.debug(d, f"   Inte hemma ({user})")
                self.notify(f"Inte hemma ({user})", title="Garageport")
        else:
            self.debug(d, "   Faulty access")
            self.notify("Du har inte inte åtkomst", title="Garageport")

        self.debug(d, f"   run_in(terminate_cb, timer={self.g_timer})")
        self.run_in(self.terminate_cb, self.g_timer)

        self.debug(d, f"return()")
        self.g_debug -= 1

    def terminate_cb(self, kwargs):
        self.g_debug += 1
        d = self.g_debug
        self.debug(d, "GaragePort:terminate(")
        self.debug(d, f"    kwargs    = {kwargs}")
        self.debug(d, ")")

        self.debug(d, f"   turn_off({self.g_init})")
        self.turn_off(self.g_init)

        self.debug(d, f"return()")
        self.g_debug -= 1

    def debug(self, debug_offset, debug_text):
        # debug_offset: the offset (1, 2, 3....)
        # debug_text  : the text
        if self.g_debug_print:
            offset = debug_offset * "    "
            self.log(f"{offset}{debug_text}")
