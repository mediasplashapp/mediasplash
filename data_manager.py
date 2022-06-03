# Copyright [2021] [mohamedSulaiman]
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json


class DataManager:
    def __init__(self, filename):
        self.filename = filename
        self.d = {}

    def exists(self, item):
        if item in self.d:
            return True
        return False

    def add(self, initial_name, content):
        self.d[initial_name] = content

    def get(self, name):
        if name in self.d:
            return self.d.get(name)
        return False

    def save(self):
        try:
            with open(self.filename, "w") as fn:
                fn.write(json.dumps(self.d))
        except FileNotFoundError:
            return False
        return True

    def load(self):
        try:
            with open(self.filename, "r") as fn:
                self.d = json.loads(fn.read())
        except FileNotFoundError:
            return False
        return True
