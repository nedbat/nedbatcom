import stellated.XuffApp
import profile, pstats
import sys

profile.run('stellated.XuffApp.XuffApp().main(sys.argv)', 'xuffprof')
p = pstats.Stats('xuffprof')
p.strip_dirs().sort_stats('cumulative').print_stats(30)
