import os
from subprocess import run

twain_file_urls = [ 
	"marktwainproject.org/xtf/tei/works/MTDP10362.xml",
	"marktwainproject.org/xtf/tei/works/MTDP10363.xml",
	"marktwainproject.org/xtf/tei/works/MTDP10364.xml"
]

output_folder = "{0}{1}output{1}".format(os.getcwd(), os.sep)

for url in twain_file_urls:
	with open(output_folder + os.path.basename(url), "w") as new_tei_file:
		response = run(["curl", url], stdout=new_tei_file)