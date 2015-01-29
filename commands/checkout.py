import sublime
from sublime_plugin import WindowCommand

from .base_command import BaseCommand

NEW_BRANCH_PROMPT = "Branch name:"


class GgCheckoutBranchCommand(WindowCommand, BaseCommand):

    def run(self):
        stdout = self.git("branch", "--no-color", "--no-column")
        branch_entries = (branch.strip() for branch in stdout.split("\n") if branch)

        # The line with the active branch will begin with an asterisk.
        self.local_inactive_branches = [branch for branch in branch_entries if not branch[0] == "*"]

        if not self.local_inactive_branches:
            self.window.show_quick_panel(["There are no branches available."], None)
        else:
            self.window.show_quick_panel(self.local_inactive_branches, self.on_selection, sublime.MONOSPACE_FONT)

    def on_selection(self, branch_name_index):
        if branch_name_index == -1:
            return

        branch_name = self.local_inactive_branches[branch_name_index]
        self.git("checkout", branch_name)
        sublime.status_message("Checked out `{}` branch.".format(branch_name))


class GgCheckoutNewBranchCommand(WindowCommand, BaseCommand):

    def run(self):
        self.window.show_input_panel(NEW_BRANCH_PROMPT, "", self.on_done, None, None)

    def on_done(self, branch_name):
        self.git("checkout", "-b", branch_name)
        sublime.status_message("Created and checked out `{}` branch.".format(branch_name))


class GgCheckoutRemoteBranchCommand(WindowCommand, BaseCommand):

    def run(self):
        self.remote_branches = self.get_remote_branches()
        self.window.show_quick_panel(self.remote_branches, self.on_selection, sublime.MONOSPACE_FONT)

    def on_selection(self, remote_branch_index):
        if remote_branch_index == -1:
            return

        remote_branch = self.remote_branches[remote_branch_index]
        local_name = remote_branch.split("/", 1)[1]
        self.git("checkout", "-b", local_name, "--track", remote_branch)
        sublime.status_message("Checked out `{}` as local branch `{}`.".format(remote_branch, local_name))