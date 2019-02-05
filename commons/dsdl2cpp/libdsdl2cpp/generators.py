#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Copyright (C) 2018-2019  UAVCAN Development Team  <uavcan.org>
# This software is distributed under the terms of the MIT License.
#

import logging
from abc import ABCMeta, abstractmethod
from datetime import datetime
from pathlib import Path, PurePath
from typing import Dict, ItemsView, KeysView, List

from jinja2 import (Environment, FileSystemLoader, Template,
                    TemplateRuntimeError, environmentfilter)
from jinja2.runtime import Undefined

from pydsdl.data_type import (CompoundType, ServiceType, StructureType,
                              UnionType)

logger = logging.getLogger(__name__)

# +---------------------------------------------------------------------------+


class Generator(metaclass=ABCMeta):

    def __init__(self, output_basedir: Path, parser_result: Dict[CompoundType, Path]):
        self._output_basedir = output_basedir
        self._parser_result = parser_result

    @property
    def input_types(self) -> KeysView[CompoundType]:
        return self._parser_result.keys()

    @property
    def parser_results(self) -> ItemsView[CompoundType, Path]:
        return self._parser_result.items()

    @abstractmethod
    def generate_all(self, is_dryrun: bool = False) -> int:
        raise NotImplementedError()

# +---------------------------------------------------------------------------+

def _jinja2_filter_yamlfy(value):
    try:
        from yaml import dump
        return dump(value)
    except ModuleNotFoundError:
        return "(pyyaml not installed)"

@environmentfilter
def _jinja2_filter_required_value(env: Environment, value):
    if type(value) is Undefined:
        raise TemplateRuntimeError("Missing required value.")
    return value

def _jinja2_filter_macrofy(value: str) -> str:
    return value.replace(' ', '_').replace('.', '_').upper()

class Jinja2Generator(Generator):

    TEMPLATE_SUFFIX = ".j2"

    def __init__(self, output_basedir: Path, parser_result: Dict[CompoundType, Path], templates_dir: Path):
        super(Jinja2Generator, self).__init__(
            output_basedir, parser_result)
        if templates_dir is None:
            raise ValueError("Tempaltes directory argument was None")
        if not Path(templates_dir).exists:
            raise ValueError(
                "Tempaltes directory {} did not exist?".format(templates_dir))
        logger.info("Loading templates from {}".format(templates_dir))
        self._env = Environment(loader=FileSystemLoader(
            [str(templates_dir)], followlinks=True))
        self._env.filters["yamlfy"] = _jinja2_filter_yamlfy
        self._env.filters["required"] = _jinja2_filter_required_value
        self._env.filters["macrofy"] = _jinja2_filter_macrofy

    def generate_all(self, is_dryrun: bool = False) -> int:
        for (parsed_type, output_path) in self.parser_results:
            self._generate_type(parsed_type, output_path, is_dryrun)
        return 0

    def _generate_type(self, input_type: CompoundType, output_path: Path, is_dryrun: bool):
        template_name = str(
            PurePath(type(input_type).__name__).with_suffix(self.TEMPLATE_SUFFIX))
        self._env.globals["now_utc"] = datetime.utcnow()
        template: Template = self._env.get_template(template_name)
        result: str = template.render(T=input_type)
        if not is_dryrun:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                output_file.write(result)
