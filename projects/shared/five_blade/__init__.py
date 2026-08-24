"""FiveEdge — original ColdBrew delivery kernel.

Five blades (REV / UNLOCK / INFIL / HARVEST / TRAINER) compiled into a
single owned prompt block.  No third-party prompt text is vendored here.
"""

from .compiler import compile_pack, compile_digest
from .router import classify, BLADE_IDS
from .blades import BLADE_SPECS

__all__ = ["compile_pack", "compile_digest", "classify", "BLADE_IDS", "BLADE_SPECS"]
