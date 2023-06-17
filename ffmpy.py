# BASED ON https://github.com/Ch00k/ffmpy

import shlex
import subprocess
import shutil
import platform
import os
import logging
import sys


class FFmpeg:
    def __init__(
        self,
        executable="ffmpeg",
        global_options=None,
        globalopts=("-v", "error", "-hide_banner", "-y"),
        inputs=None,
        outputs=None,
        check=False,
    ):
        if shutil.which(executable):
            self.executable = shutil.which(executable)
        else:
            self.executable = os.path.join(os.path.dirname(sys.executable), executable)
        self._cmd = [self.executable]
        if global_options:
            global_options = globalopts + global_options
        else:
            global_options = globalopts
        global_options = global_options or []
        if _is_sequence(global_options):
            normalized_global_options = []
            for opt in global_options:
                normalized_global_options += shlex.split(opt)
        else:
            normalized_global_options = shlex.split(global_options)

        self._cmd += normalized_global_options
        self._cmd += _merge_args_opts(inputs, add_input_option=True)
        self._cmd += _merge_args_opts(outputs)

        self.cmd = subprocess.list2cmdline(self._cmd)
        self.process = None
        self.check = check

    def run(self, input_data=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=None):
        self.process = subprocess.Popen(
            self._cmd,
            stdout=stdout,
            stderr=stderr,
            env=env,
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0,
            text=True,
            encoding="utf-8",
            errors="strict",
        )
        out = list(self.process.communicate())
        if self.process.returncode != 0 and self.check:
            raise subprocess.CalledProcessError(
                self.process.returncode,
                self.process.args,
                out[0],
                out[1],
            )
        logging.debug(f"process {self.process} with {self.process.args} done with output: {out[0]}\n{out[1]}")
        for index, item in enumerate(out):
            if item and isinstance(item, str):
                out[index] = item.strip()
        return out

    def destroy(self):
        self.process.stdout.close()
        self.process.stderr.close()
        self.process.wait()


class FFprobe(FFmpeg):
    def __init__(
        self,
        executable="ffprobe",
        global_options=None,
        globalopts=("-v", "error", "-hide_banner"),
        inputs=None,
    ):
        super(FFprobe, self).__init__(
            executable=executable,
            global_options=global_options,
            globalopts=globalopts,
            inputs=inputs,
        )


def _is_sequence(obj):
    return hasattr(obj, "__iter__") and not isinstance(obj, str)


def _merge_args_opts(args_opts_dict, **kwargs):
    merged = []

    if not args_opts_dict:
        return merged

    for arg, opt in args_opts_dict.items():
        if not _is_sequence(opt):
            opt = shlex.split(opt or "")
        merged += opt

        if not arg:
            continue

        if "add_input_option" in kwargs:
            merged.append("-i")

        merged.append(arg)

    return merged
