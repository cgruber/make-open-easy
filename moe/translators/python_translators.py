#!/usr/bin/env python
#
# Copyright 2011 Google Inc. All Rights Reserved.

"""Tools to translate codebases in one project space into another.

A central concept of MOE is the Project Space. One project leads different lives
in different repositories. (E.g., it needs a Makefile in the public project,
and a different type of build file internally.) Translators let us take a
codebase in the internal project space and generate a codebase in the public
project space.

"""

__author__ = 'jwall@google.com (Jeremy Wall)'


import os
import tempfile

import json as simplejson

from google.apputils import resources

from moe import base
from moe import codebase_utils
from moe import moe_app
from moe.translators import translators


TWO_TO_THREE_DRIVER = """#!/usr/bin/env python
import sys
from lib2to3.main import main

sys.exit(main("lib2to3.fixes"))"""

class TwoToThreeTranslator(translators.Translator):
  """A translator that invokes the MOE scrubber to translate."""

  def __init__(self, from_project_space, to_project_space):
    translators.Translator.__init__(self)
    self._from_project_space = from_project_space
    self._to_project_space = to_project_space

  def FromProjectSpace(self):
    return self._from_project_space

  def ToProjectSpace(self):
    return self._to_project_space

  def Translate(self, codebase):
    (output_bin_fd, output_bin_filename) = tempfile.mkstemp(
        dir=moe_app.RUN.temp_dir)
    os.write(output_bin_fd, TWO_TO_THREE_DRIVER)
    os.close(output_bin_fd)
    base.SetExecutable(output_bin_filename)
    task = moe_app.RUN.ui.BeginImmediateTask(
      'translate',
      'Translating from %s project space to %s (using python 2to3)' %
      (self._from_project_space, self._to_project_space))

    with task:
        modified_codebase = codebase_utils.CreateModifiableCopy(codebase)
        base.RunCmd(output_bin_filename, ['--write', '--nobackups', '--verbose',
                                          modified_codebase.Path()])
        os.remove(output_bin_filename)
        return modified_codebase

class ThreeToTwoTranslator(translators.Translator):
  """A translator that invokes the MOE scrubber to translate."""

  def __init__(self, from_project_space, to_project_space):
    translators.Translator.__init__(self)
    self._from_project_space = from_project_space
    self._to_project_space = to_project_space

  def FromProjectSpace(self):
    return self._from_project_space

  def ToProjectSpace(self):
    return self._to_project_space

  def Translate(self, codebase):
    task = moe_app.RUN.ui.BeginImmediateTask(
      'translate',
      'Translating from %s project space to %s (using python 3to2)' %
      (self._from_project_space, self._to_project_space))

    with task:
        modified_codebase = codebase_utils.CreateModifiableCopy(codebase)
        base.RunCmd('3to2', ['--write', '--nobackups',
                                          modified_codebase.Path()])
        return modified_codebase
