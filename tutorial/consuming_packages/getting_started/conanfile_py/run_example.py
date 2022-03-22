import os
import platform
import subprocess
from contextlib import contextmanager


@contextmanager
def chdir(dir_path):
    current = os.getcwd()
    os.chdir(dir_path)
    try:
        yield
    finally:
        os.chdir(current)


def run(cmd, error=False):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    out = out.decode("utf-8")
    err = err.decode("utf-8")
    ret = process.returncode

    output = err + out
    print("------------")
    print("Running: {}".format(cmd))
    print(output)
    print("------------")
    if ret != 0 and not error:
        raise Exception("Failed cmd: {}\n{}".format(cmd, output))
    if ret == 0 and error:
        raise Exception(
            "Cmd succeded (failure expected): {}\n{}".format(cmd, output))
    return output

configuration = "Release"
build_folder = "build" if platform.system() == "Windows" else f"cmake-build-{configuration.lower()}"
run(f"conan install . --build missing")
run(f"cd {build_folder}")
with chdir(f"{build_folder}"):
    source_command = "" if platform.system() == "Windows" else ". ./"
    extension = ".bat" if platform.system() == "Windows" else ".sh"
    run_exe = f"{configuration}\compressor.exe" if platform.system() == "Windows" else "./compressor"
    cmake_win = f"cmake .. -G \"Visual Studio 15 2017\" -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake && cmake --build . --config {configuration}"
    cmake_other = "cmake .. -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake && cmake --build . "
    cmake_cmd = cmake_win if platform.system() == "Windows" else cmake_other
    if platform.system() == "Windows":
        out = run(f"{cmake_cmd}")
    else:
        out = run(f"{source_command}conanbuild{extension} && {cmake_cmd} && {source_command}deactivate_conanbuild{extension}")

    run(run_exe)
