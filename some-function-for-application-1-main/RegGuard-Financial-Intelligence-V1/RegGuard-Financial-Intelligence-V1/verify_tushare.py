"""Optional bounded diagnostic. No token is printed or written to a file."""
import sys
from alphapilot.competition_tushare import probe_permissions
if __name__=='__main__':
    print(probe_permissions(sys.argv[1] if len(sys.argv)>1 else '000001.SZ'))
