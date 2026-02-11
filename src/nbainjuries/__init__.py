import jpype.imports
from tabula.backend import jar_path

# Pre-load JVM configs
jpype.addClassPath(jar_path())
if not jpype.isJVMStarted():
    jvmpath = jpype.getDefaultJVMPath()
    java_opts = ["-Dfile.encoding=UTF-8", "-Xrs"]
    jpype.startJVM(jvmpath, *java_opts, convertStrings=False)

from importlib.metadata import version
from . import injury, injury_asy

__version__ = version(__package__)
__all__ = ["injury", "injury_asy"]
