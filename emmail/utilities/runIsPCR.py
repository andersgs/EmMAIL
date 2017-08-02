from os import remove, environ
import logging

from emmail.objects.IsPCR import IsPCR
from emmail.objects.BLAST import BLAST

logging.basicConfig(level=environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__name__)

def buildSubparser(parser):
    """
    Add arguments to the subparser, and return the subparser.
    """
    parser.add_argument("--primer", required=True, type=str,
                        help="PCR primer. Text file with 3 columns: Name, Forward Primer, Reverse Primer.")
    
    parser.add_argument("--query", required=True, type=str,
                        help="The genome to PCR against.")
    parser.add_argument("--db", required=True, type=str,
                        help="The database to BLAST PCR product against.")

    # isPcr options
                      
    parser.add_argument("-minPerfect", default=15, type=int,
                        help="Minimum size of perfect match at 3' primer end. Default is 15.")
    parser.add_argument("-minGood", default=15, type=int,
                        help=("Minimum size where there must be 2 matches for each mismatch. "
                              "Default is 15; there must be 10 match in 15bp primer size."))
    parser.add_argument("-minSize", default=0, type=int,
                        help="Minimum size of PCR product. Default is 0.")
    parser.add_argument("-maxSize", default=4000, type=int,
                        help="Maximum size of PCR product. Default is 4000.")
    
    parser.add_argument("-outPCR", default="pcr.tmp", type=str, 
                        help="Output filename, to use as BLAST query. Default to pcr.tmp.")  
    
    parser.add_argument("-savePCR", default=False, action="store_true",
                        help="Temporary isPcr output \"pcr.tmp\" will not be removed on mention.")
    
    # BLAST options

    parser.add_argument("-dust", default="no", type=str,
                        help="Filter query sequence with DUST. Default no.")
    parser.add_argument("-perc_identity", default=95, type=int,
                        help="Minimal percent identity of sequence. Default is 95.")
    parser.add_argument("-culling_limit", default=1, type=int,
                        help="Total hits to return in a position. Default is 1.")
    parser.add_argument("-outBLAST", default="None", 
                        action="store", type=str,
                        help="File to stream BLAST output. Default to terminal.")

    parser.add_argument("-add_header", action="store_true", default=False,
                        help="Add header to the output file on mention.")
    
    # Row options
    
    parser.add_argument("-mismatch", default=4, type=int,
                        help="Threshold for number of mismatch to allow in BLAST hit. Default is 4.")
    parser.add_argument("-align_diff", default=5, type=int,
                        help="Threshold for difference between alignment length and subject length in BLAST hit. Default is 5.")                        
    parser.add_argument("-gap", default=2, type=int,
                        help="Threshold gap to allow in BLAST hit. Default is 2.")
                        
    return parser
    
def main(args):
    
    pcr = IsPCR(assembly_filename = args.query,
                primer_filename = args.primer,
                min_perfect = args.minPerfect,
                min_good = args.minGood,
                # min_product_length = args.minSize,
                max_product_length = args.maxSize,
                output_stream = "stdout")
    
    # Run isPcr, take output and use it as input for Blast.
    with open(args.outPCR, "w") as temp:
        temp.write(pcr.run_isPCR())
    
    blast = BLAST(db = args.db, 
                    query = args.outPCR, 
                    dust = args.dust, 
                    perc_identity = args.perc_identity,
                    culling_limit = args.culling_limit, 
                    output_stream = args.outBLAST,
                    header = args.add_header,
                    
                    mismatch = args.mismatch,
                    align_diff = args.align_diff,
                    gap = args.gap)
                    
    blast.run_blastn_pipeline()
    
    if args.savePCR == False:
        remove(args.outPCR)
        logger.info("{} is removed from directory".format(args.outPCR))
    
    else:
        logger.info("{} is kept on directory".format(args.outPCR))
        
    logger.info("Result for {} is saved as {}".format(args.query.split("/")[-1], args.outBLAST))