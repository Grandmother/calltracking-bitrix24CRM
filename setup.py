#!/usr/bin/env python

from setuptools import setup

setup( name = "calltracking-bitrix24CRM",
       version = "0.1.0",
       description = "The script, that allows to export calls from calltracking.ru service to bitrix24 CRM",
       url = "https://github.com/Grandmother/calltracking-bitrix24CRM",
       author = "Roman Kovtyukh",
       author_email = "HelloDearGrandma@gmail.com",
       license = "MIT",
       scripts = ['bin/calltracking_bitrix'],
       install_requieres = ['bitrix24-python-sdk',
                            'phonenumbers',
                            'pysmsru'])