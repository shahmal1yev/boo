import zipfile
import unittest
import os
from tempfile import TemporaryDirectory

import exceptions
from file import Plugin, Zip

class TestPluginMethods(unittest.TestCase):

    def setUp(self):
        self.test_dir = TemporaryDirectory()
        self.plugin_path = os.path.join(self.test_dir.name, 'test_plugin')
        os.makedirs(self.plugin_path)

        self.main_file_path = os.path.join(self.plugin_path, 'init.php')
        with open(self.main_file_path, 'w') as f:
            f.write("""
<?php
/**
  * Plugin Name: Plugin Name
  * Version: 1.0.0
*/
            """)

        self.another_plugin_path = os.path.join(self.test_dir.name, 'another_plugin')
        os.makedirs(self.another_plugin_path)
        self.another_main_file_path = os.path.join(self.another_plugin_path, 'init.php')
        with open(self.another_main_file_path, 'w') as f:
            f.write("""
<?php
/**
  * Plugin Name: Another Plugin
  * Version: 1.0.0
*/
            """)

        self.invalid_plugin_path = os.path.join(self.test_dir.name, 'invalid_plugin')
        os.makedirs(self.invalid_plugin_path)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_abspaths(self):
        abspaths = Plugin.abspaths(self.test_dir.name)
        expected_paths = sorted([
            self.plugin_path,
            self.another_plugin_path
        ])
        self.assertEqual(abspaths, expected_paths)

        empty_dir = os.path.join(self.test_dir.name, 'empty_dir')
        os.makedirs(empty_dir)
        abspaths = Plugin.abspaths(empty_dir)
        self.assertEqual(abspaths, [])

    def test_main_file(self):
        self.assertEqual(Plugin.main_file(self.plugin_path), os.path.basename(self.main_file_path))

        with self.assertRaises(exceptions.SearchNotFound):
            Plugin.main_file(self.invalid_plugin_path)

    def test_filter_include(self):
        all_paths = [self.plugin_path, self.another_plugin_path]

        include = ['test_plugin']
        filtered_paths = Plugin.filter(all_paths, include=include, exclude=[])
        self.assertEqual(filtered_paths, [self.plugin_path])

        include = []
        filtered_paths = Plugin.filter(all_paths, include=include, exclude=[])
        self.assertEqual(filtered_paths, all_paths)

    def test_filter_exclude(self):
        all_paths = [self.plugin_path, self.another_plugin_path]

        exclude = ['another_plugin']
        filtered_paths = Plugin.filter(all_paths, include=[], exclude=exclude)
        self.assertEqual(filtered_paths, [self.plugin_path])

        exclude = []
        filtered_paths = Plugin.filter(all_paths, include=[], exclude=exclude)
        self.assertEqual(filtered_paths, all_paths)

    def test_update(self):
        plugin = Plugin(self.plugin_path)
        new_content = """
<?php
/**
  * Plugin Name: Updated Plugin
  * Version: 2.0.0
*/
        """
        plugin.update(new_content)
        with open(self.main_file_path, 'r') as f:
            content = f.read()
        self.assertEqual(content.strip(), new_content.strip())

        invalid_plugin = Plugin(self.invalid_plugin_path)
        with self.assertRaises(exceptions.BooException):
            invalid_plugin.update(new_content)

    def test_content(self):
        plugin = Plugin(self.plugin_path)
        with open(self.main_file_path, 'r') as f:
            expected_content = f.read()
        self.assertEqual(plugin.content().strip(), expected_content.strip())

        invalid_plugin = Plugin(self.invalid_plugin_path)
        with self.assertRaises(exceptions.BooException):
            invalid_plugin.content()

    def test_list(self):
        plugins = Plugin.list(self.test_dir.name)
        self.assertEqual(len(plugins), 2)
        self.assertTrue(any(p.path == self.plugin_path for p in plugins))
        self.assertTrue(any(p.path == self.another_plugin_path for p in plugins))

        empty_dir = os.path.join(self.test_dir.name, 'empty_dir')
        os.makedirs(empty_dir)
        plugins = Plugin.list(empty_dir)
        self.assertEqual(plugins, [])


class TestZipMethods(unittest.TestCase):

    def setUp(self):
        self.test_dir = TemporaryDirectory()
        self.subdir = os.path.join(self.test_dir.name, 'subdir')
        os.makedirs(self.subdir)

        self.file1 = os.path.join(self.test_dir.name, 'file1.txt')
        self.file2 = os.path.join(self.subdir, 'file2.txt')

        with open(self.file1, 'w') as f:
            f.write("This is file 1")

        with open(self.file2, 'w') as f:
            f.write("This is file 2")

        self.zip_path = os.path.join(self.test_dir.name, 'output.zip')

    def tearDown(self):
        self.test_dir.cleanup()

    def test_create_zip(self):
        Zip.create(self.test_dir.name, self.zip_path)

        self.assertTrue(os.path.exists(self.zip_path))

        with zipfile.ZipFile(self.zip_path, 'r') as zip_file:
            zip_file_names = zip_file.namelist()

            test_dir_name = os.path.basename(self.test_dir.name)

            # Check the content of the zip file
            self.assertIn(os.path.join(test_dir_name, 'subdir/file2.txt'), zip_file_names)
            self.assertIn(os.path.join(test_dir_name, 'file1.txt'), zip_file_names)

            with zip_file.open(os.path.join(test_dir_name, 'subdir/file2.txt')) as f:
                self.assertEqual(f.read().decode(), "This is file 2")

            with zip_file.open(os.path.join(test_dir_name, 'file1.txt')) as f:
                self.assertEqual(f.read().decode(), "This is file 1")
