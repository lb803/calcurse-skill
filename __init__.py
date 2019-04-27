#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  Luca Baffa - lb803@mailbox.org

from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder
#~ from mycroft.util.log import LOG

import re
from subprocess import run, PIPE

class Calcurse(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_handler(IntentBuilder('read')
        .require('what')
        .require('calendar'))
    def handle_read(self, message):
        # Retrieve appointments
        cmd = run(['calcurse', '-a',
                   '--format-apt= - %m (from %S to %E)\n',
                   '--format-recur-apt= * %m (from %S to %E)\n'],
                  stdout=PIPE)

        data = cmd.stdout.decode('utf-8').split('\n')

        day_apt = []
        timed_apt = []

        re_day_apt = re.compile('^ \* (?P<apt>.*)')
        re_timed_apt = re.compile('^ - (?P<apt>.[^(]*) \(from (?P<start>[0-9]+:[0-9]+) to (?P<end>[0-9]+:[0-9]+)\)')

        for apt in data:
            match_day_apt = re_day_apt.match(apt)
            if match_day_apt:
                day_apt.append(match_day_apt.group('apt'))
                continue;

            match_timed_apt = re_timed_apt.match(apt)
            if match_timed_apt:
                timed_apt.append({'apt': match_timed_apt.group('apt'),
                                  'start': match_timed_apt.group('start')})

        for apt in day_apt:
            self.speak_dialog('read.day_apt', {'apt': apt})

        for apt in timed_apt:
            self.speak_dialog('read.timed_apt', {'apt': apt['apt'],
                                                 'start': apt['start']})

        if len(day_apt) == 0 and len(timed_apt) == 0:
            self.speak_dialog('no.apt')


def create_skill():
    return Calcurse()

