# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys

import yaml

from fleetrec.core.utils import envs

trainer_abs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trainers")
trainers = {}


def trainer_registry():
    trainers["SingleTrainer"] = os.path.join(trainer_abs, "single_trainer.py")
    trainers["ClusterTrainer"] = os.path.join(trainer_abs, "cluster_trainer.py")
    trainers["CtrCodingTrainer"] = os.path.join(trainer_abs, "ctr_coding_trainer.py")
    trainers["CtrModulTrainer"] = os.path.join(trainer_abs, "ctr_modul_trainer.py")


trainer_registry()


class TrainerFactory(object):
    def __init__(self):
        pass

    @staticmethod
    def _build_trainer(yaml_path):
        print(envs.pretty_print_envs(envs.get_global_envs()))

        train_mode = envs.get_trainer()
        trainer_abs = trainers.get(train_mode, None)

        if trainer_abs is None:
            if not os.path.exists(train_mode) or not os.path.isfile(train_mode):
                raise ValueError("trainer {} can not be recognized".format(train_mode))
            trainer_abs = train_mode
            train_mode = "UserDefineTrainer"

        train_dirname = os.path.dirname(trainer_abs)
        base_name = os.path.splitext(os.path.basename(trainer_abs))[0]
        sys.path.append(train_dirname)
        trainer_class = envs.lazy_instance(base_name, train_mode)
        trainer = trainer_class(yaml_path)
        return trainer

    @staticmethod
    def create(config):
        _config = None
        if os.path.exists(config) and os.path.isfile(config):
            with open(config, 'r') as rb:
                _config = yaml.load(rb.read(), Loader=yaml.FullLoader)
        else:
            raise ValueError("fleetrec's config only support yaml")

        envs.set_global_envs(_config)
        trainer = TrainerFactory._build_trainer(config)
        return trainer


# server num, worker num
if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("need a yaml file path argv")
    trainer = TrainerFactory.create(sys.argv[1])
    trainer.run()
