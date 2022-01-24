# ################################################################### #
#                                                                     #
#  BigBrotherBot(B3) (www.bigbrotherbot.net)                          #
#  Copyright (C) 2005 Michael "ThorN" Thornton                        #
#                                                                     #
#  This program is free software; you can redistribute it and/or      #
#  modify it under the terms of the GNU General Public License        #
#  as published by the Free Software Foundation; either version 2     #
#  of the License, or (at your option) any later version.             #
#                                                                     #
#  This program is distributed in the hope that it will be useful,    #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of     #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the       #
#  GNU General Public License for more details.                       #
#                                                                     #
#  You should have received a copy of the GNU General Public License  #
#  along with this program; if not, write to the Free Software        #
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA      #
#  02110-1301, USA.                                                   #
#                                                                     #
# ################################################################### #
__author__ = 'donna30' 
__version__ = '1.0'

import b3
import b3.events
import b3.plugin

class PbdisarmPlugin(b3.plugin.Plugin):

    requiresConfigFile = False

    GUNS =  ["knife", "beretta", "deagle", "spas12", "mp5k", 
            "ump45", "hk69", "lr", "g36", "psg1", "he", "smoke", 
            "sr8", "ak103", "negev", "m4", "glock", "colt", 
            "mac11", "frf1", "benelli", "p90", "magnum", "fstod"]

    GAME_PATH = None

    def onStartup(self):
        self._adminPlugin = self.console.getPlugin('admin')

        # We cannot start without the admin plugin
        if not self._adminPlugin:
            self.error('Could not find admin plugin')
            return

        # Registering events
        self.registerEvent(self.console.getEventID('EVT_CLIENT_JOIN'), self.onJoin)
        self.registerEvent(self.console.getEventID('EVT_CLIENT_SPAWN'), self.onSpawn)

        # Registering commands
        self._adminPlugin.registerCommand(self, 'disarm', 60, self.cmd_disarm)
        self._adminPlugin.registerCommand(self, 'arm', 60, self.cmd_arm)

        # Setting the path
        self.GAME_PATH = self.console.config.getpath('server', 'game_log').replace('games.log', "")
        
    def onJoin(self, event):
        client = event.client
        self.check_disarm(client)

    def onSpawn(self, event):
        client = event.client
        self.check_disarm(client)

    def check_disarm(self, client):
        if client.bot:
            self.debug('Bot')
        else:
            cursor = self.console.storage.query('SELECT * FROM pbdisarm WHERE iduser = %s' % client.id)
            if cursor.rowcount == 0:
                cursor.close()
                return
            else:
                cursor.close()
                self.disarm_client(client)

    def cmd_disarm(self, data, client, cmd=None):
        handler = self._adminPlugin.parseUserCmd(data)
        sclient = self._adminPlugin.findClientPrompt(handler[0], client)

        if not data:
            client.message('^5!disarm ^6<client>')
            return

        cursor = self.console.storage.query('SELECT * FROM pbdisarm WHERE iduser = %s' % client.id)
        if cursor.rowcount == 0:
            self.disarm_client(sclient)
            sclient.message('^3You were ^1PERMANENTLY DISARMED ^3by an ^2Admin')
            cursor = self.console.storage.query('INSERT INTO pbdisarm (iduser) VALUES (%i)' % sclient.id)
            cursor.close()
        else:
            client.message('^3Client already disarmed')
            cursor.close()

    def cmd_arm(self, data, client, cmd=None):
        handler = self._adminPlugin.parseUserCmd(data)
        sclient = self._adminPlugin.findClientPrompt(handler[0], client)

        if not sclient:
            return
    
        self.console.storage.query('DELETE FROM pbdisarm WHERE iduser = %s' % sclient.id)
        client.message('^2Armed ^5%s' % sclient.name)
        sclient.message('^3You were ^2re-armed ^3by an ^5Admin')

    def disarm_client(self, client):
        fileloc = "%s/pbdisarm_helper.txt" % self.GAME_PATH
        with open(fileloc, "w") as file:
            for i in self.GUNS:
                file.write("rw %s %s\n" % (client.cid, i))
        self.console.write("exec pbdisarm_helper.txt")
