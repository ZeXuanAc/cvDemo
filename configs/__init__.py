# -*- coding:utf-8 -*-
import os
import logging.config

logging.config.fileConfig(os.path.join(os.path.dirname(os.path.realpath(__file__)), "logger.conf"))  # 采用配置文件
LOGGER = logging.getLogger("file")
