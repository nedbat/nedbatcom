#import stellated.XuffApp
from djstell.bin.makehtml import CmdLine
import profile, pstats
import sys

profile.run('CmdLine().main(sys.argv[1:])', 'profmake')
p = pstats.Stats('profmake')
p.strip_dirs().sort_stats('cumulative').print_stats(30)
