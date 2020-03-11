from PyInstaller import log as logging
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

logger = logging.getLogger(__name__)
logger.info("  - custom hook to fix Tensorflow forwarding to `tensorflow_core`")
hiddenimports = collect_submodules("tensorflow_core")
datas = collect_data_files("tensorflow_core", subdir=None, include_py_files=True)
# print(hiddenimports)
# print(datas)
