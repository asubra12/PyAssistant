import subprocess
from difflib import SequenceMatcher
import os
import signal


class ApplicationPuppet:
    """
    Class to manipulate various applications
    To eventually be integrated with voice recognition
    """

    def __init__(self):
        """
        Initialize inherent variables
        """
        self.processes = []

        p = subprocess.Popen(["ls", "/Applications/"], stdout=subprocess.PIPE)
        self.appNames = p.communicate()[0].decode("utf-8").split("\n")
        return

    @staticmethod
    def get_app_name(app_names_list, app):
        """
        Get the true application name from an inputted phrase
        Designed to find the closest app, account for poor listening

        :param app_names_list: list of all apps on this machine, calculated in init
        :param app: String, app to open
        :return: String, actual name of app to open (ie. Notepad.app)
        """
        most_similar = 0.0
        app_to_open = None

        for app_name in app_names_list:
            app_name_trimmed = app_name.split('.app')[0].lower()
            similarity = SequenceMatcher(None, app_name_trimmed, app.lower()).ratio()

            if similarity > most_similar:
                app_to_open = app_name
                most_similar = similarity

        return app_to_open

    @staticmethod
    def kill(process):
        """
        Kill a given process
        For some reason, the pid of the application itself is 1 more than the pid of the subprocess

        When evaluating a stack of commands, need a 1s delay between opening applications
            Otherwise pid might be two off go figure

        :param process: subprocess object
        :return Nothing
        """
        os.killpg(process.pid+1, signal.SIGKILL)
        return

    def start_app(self, app_to_open, new_instance_command=False):
        """
        Open a given app
        Must be within applications folder

        Append the opened process to processes list


        :param app_to_open: string, eventually parsed from language, of app to open
        :param new_instance_command: Bool, whether or not to force a new instance opening
        :return: Return the process that was opened
        """
        true_app_name = self.get_app_name(self.appNames, app_to_open)
        activity_monitor_app_name = true_app_name.split('.app')[0]

        new_instance = new_instance_command or not self.is_running(activity_monitor_app_name)

        if new_instance:
            process = subprocess.Popen(["open", "-n", "-W", "/Applications/" + true_app_name],
                                       stdout=subprocess.PIPE,
                                       shell=False)
        else:
            process = subprocess.Popen(["open", "-W", "/Applications/" + true_app_name],
                                       stdout=subprocess.PIPE,
                                       shell=False)
        self.processes.append(process)
        return process

    @staticmethod
    def is_running(app_name):
        """
        Check if an application is currently running

        :param app_name: name of application to check (in activity monitor)
        :return: Bool T/F if running or not
        """
        count = int(subprocess.check_output(["osascript",
                                             "-e", "tell application \"System Events\"",
                                             "-e", "count (every process whose name is \"" + app_name + "\")",
                                             "-e", "end tell"]).strip())
        return count > 0

    def kill_last(self):
        """
        Kill the last opened process
        Should be useful for bugtesting in the future
            Ie. No don't open that

        :return: Nothing
        """
        killed = False
        while len(self.processes) > 0 and not killed:
            last_process_opened = self.processes.pop()
            try:
                self.kill(last_process_opened)
                killed = True
            except ProcessLookupError:
                pass
        return

    def kill_specific_app(self, app_to_kill):
        """
        Kill all instances of a specific app

        :param app_to_kill: app name to kill, string, matched with actual application
        :return: Nothing
        """
        true_app_name = self.get_app_name(self.appNames, app_to_kill)
        subprocess.call(['osascript', '-e', 'tell application "' + true_app_name + '" to quit'])
        return



