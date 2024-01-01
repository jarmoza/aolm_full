from backports.shutil_get_terminal_size import get_terminal_size

debug_character = "#"
debug_divider = debug_character * get_terminal_size().__dict__["columns"]



class bcolors:

	
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def debug_print(p_string):
	print "{0}{1}{2}\n{3}{4}{2}".format(bcolors.OKGREEN, p_string, bcolors.ENDC, 
									    bcolors.OKBLUE, debug_divider)

def main():

	print "{0}I'm a header{1}".format(bcolors.HEADER, bcolors.ENDC)
	print "{0}I'm blue okay{1}".format(bcolors.OKBLUE, bcolors.ENDC)
	print "{0}I'm green okay{1}".format(bcolors.OKGREEN, bcolors.ENDC)
	print "{0}I'm a warning{1}".format(bcolors.WARNING, bcolors.ENDC)
	print "{0}I'm a failure{1}".format(bcolors.FAIL, bcolors.ENDC)
	print "{0}I'm bold{1}".format(bcolors.BOLD, bcolors.ENDC)
	print "{0}I'm underlined{1}".format(bcolors.UNDERLINE, bcolors.ENDC)


if "__main__" == __name__:
	main()

