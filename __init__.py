#
# Description:
# This is a Binary Ninja plugin that allows you to decompile all the codebase in
# HLIL, so that you can do interesting things at the source level.
#
# Author:
# Wei Chen (atxsinn3r)
# https://github.com/atxsinn3r/BinjaHLILDump
#
from binaryninja import *
import re
import platform

class HlilDump(BackgroundTaskThread):
  def __init__(self, bv, dest):
    BackgroundTaskThread.__init__(self, 'Dumping HLIL...', True)
    self.bv = bv
    self.dest = dest

  def normalize_path(self, path):
    if 'Windows' in platform.system():
      # https://gist.github.com/doctaphred/d01d05291546186941e1b7ddc02034d3
      return re.sub(r'[><:"/\\|\?\*]', '_', path)
    else:
      return re.sub(r'/', '_', path)

  def run(self):
    count = 1
    print("Number of functions to decompile: %d" %(len(self.bv.functions)))
    for function in self.bv.functions:
      function_name = "sub_%x" %(function.start)
      symbol = self.bv.get_symbol_at(function.start)
      if hasattr(symbol, 'short_name'):
        func_short_name = symbol.short_name
        if len(self.dest) + len(func_short_name) <= 255:
          function_name = func_short_name

      print("Dumping function: %s" %(function_name))
      self.progress = "Dumping HLIL: %d/%d" %(count, len(self.bv.functions))
      source = '\n'.join(map(str, function.hlil.root.lines))
      dest_name = os.path.join(self.dest, self.normalize_path(function_name))
      f = open(dest_name, 'wb')
      f.write(bytes(source, 'utf-8'))
      f.close()
      count += 1
    print('Done.')

def dump_hlil(bv, function):
  dest = get_directory_name_input('Destination')
  if dest == None:
    print('No destination directory provided to save the decompiled source')
    return
  dump = HlilDump(bv, dest)
  dump.start()

PluginCommand.register_for_address('HLIL Dump', 'Dumps HLIL for the whole code base', dump_hlil)
