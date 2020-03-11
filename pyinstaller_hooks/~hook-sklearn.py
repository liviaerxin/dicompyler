from PyInstaller import log as logging
from PyInstaller.utils.hooks import collect_dynamic_libs

logger = logging.getLogger(__name__)
logger.info("  - custom hook to fix vcomp140.dll being skipped in bundling")
binaries = collect_dynamic_libs("sklearn")
# print(binaries)
