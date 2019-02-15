# encoding: UTF-8
import unittest

from actionwords import Actionwords
import os
test_issue_file = 'samples/inputs/issue.json'
test_dset_file = 'samples/inputs/datasets.txt'
extra_dset_file = 'samples/inputs/extra_datasets.txt'


class TestESDocERRATA(unittest.TestCase):


    def setUp(self):
        self.actionwords = Actionwords(test_issue_file=test_issue_file, test_dset_file=test_dset_file)

    def test_Saving_credentials(self):
        self.actionwords.save_credentials()
        self.assertTrue(self.actionwords.check_credentials(True))
        self.actionwords.reset_credentials()

    def test_Changing_passphrase(self):

        self.actionwords.save_credentials()
        self.actionwords.reset_passphrase()
        self.assertTrue(self.actionwords.check_credentials(False))
        self.actionwords.reset_credentials()

    def creating_an_issue_for_a_number_of_datasets(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        check_issue_files_and_pid(self)

    def updating_issue_add_some_datasets(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        self.actionwords.extra_dsets = extra_dset_file
        self.actionwords.add_dsets_to_file()
        self.actionwords.update_issue()
        check_issue_files_and_pid(self)

    def test_Updating_issue_Removing_some_datasets(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        self.actionwords.remove_dsets_from_file()
        self.actionwords.update_issue()
        check_issue_files_and_pid(self)

    def test_Updating_issue_Changing_status(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        self.actionwords.change_status()
        self.actionwords.update_issue()
        check_issue_files(self)

    def test_Updating_issue_Changing_severity(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        self.actionwords.change_severity()
        self.actionwords.update_issue()
        check_issue_files(self)

    def test_Updating_issue_Altering_description(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        self.actionwords.change_description()
        self.actionwords.update_issue()
        check_issue_files(self)

    def test_Closing_issue(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        self.actionwords.close_issue()
        self.actionwords.check_issue_files()
        check_issue_files(self)

    def test_check_pid_utilitites(self):
        self.actionwords.check_pid_utilitites()


def check_issue_files(test_case):
    test_case.assertTrue(test_case.actionwords.check_issue_files())


if __name__ == '__main__':
    unittest.main()
