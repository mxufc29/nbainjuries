import jpype
import jpype.imports
from tabula.backend import jar_path

# Pre-load JVM configs
jpype.addClassPath(jar_path())
if not jpype.isJVMStarted():
    jvmpath = jpype.getDefaultJVMPath()
    java_opts = ["-Dfile.encoding=UTF-8", "-Xrs"]
    jpype.startJVM(jvmpath, *java_opts, convertStrings=False)

from . import injury, injury_asy

__version__ = '0.5.0'
__all__ = ['injury', 'injury_asy']
