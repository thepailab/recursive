# Identification of recursive splice sites using metabolic labeling data

Three independent methods for identification of recursive splice sites from RNA-seq data are developed:

- RatchetJunction, A previously described method using splice junction reads,
- RatchetPair, which uses paired end reads straddling a splice junction,
- RatchetScan, which infers recursive splice site locations from patterns in the read coverage of introns.

## General Notes.
The scripts load_genome.py and get_motifs.py are used throughout, add sjr/core_pipeline to PYTHONPATH or copy these files into working directory
Code for aligning reads is not included in this repository. We used hisat2 with default settings in our study, but feel free to use your favorite *spliced-read* aligner.

## Defining Intron Set.
Scripts to make introns from GTF file and get coverage data are in sequence/coverage.

1. Download a gtf file for the organism you are studying.
2. Extract just the 'exon' entries and sort them by transcript name.
3. Run "cat <file>.gtf | get_introns.py > introns.bed" to parse the GTF file into a bed file of 1000+ base pair introns
4. Run "python get_intron_expression.py reads.bam introns.bed > intron_expression.bed" to obtain a pileup of coverage at each postion + number of sjr spanning intron
5. Merge coverage data from mulitple BAM files using merge.py.

## Preparing Coverage for RatchetScan.
Still in sequence/coverage.

remove_exons.sh does everything, note that this script contains hardcoded paths, so you will have to edit it... workflow is:
a. Extract reads in different size ranges.
b. Use bedtools subtract to remove exonic regions
c. Merge together intronic regions, summing the sjr counts
d. Recompute coverage of each intronic segment for all replicates
e. Merged all replicate expression levels together
f. Replace expression values in repeat regions with average of neighboring regions.

## Running RatchetScan.
All scripts are in sawtooth/mcmc_core.

run.sh will run all steps of the RatchetScan pipeline. Substeps are

a. run_mcmc.py feeds coverage data into mcmc.py. tunable parameters are set in run_mcmc.py, they are currently set as we used in our study.
b. call_sites.py transforms the MCMC probabilities into RS predicitons. setting here to instead produce random peaks for FDR analysis
c. merge_sites.py merges individual sites implicated by seperate peaks

## Running RatchetJunction and RatchetPair.
All necessary scripts are in sjr/core_pipeline/.

run_all.sh will run all steps of both pipelines. Substeps are

a. Extract reads that potentially straddle recursive splice junctions.
b. Extract putative recursive splice junction reads
c. Group putative recursive splice junction reads that have shared a 5'ss
d. Merge together data from all timepoints and replicates
e. Run RatchetPair algorithm (See straddle_gem.py).
f. Assign groups of reads to an intron based on intron expression levels

## Combining output of methods
Use combine/standard_table.py to create a combined table of graveley events, sawtooth events, and sjr detected sites
... read through to replace hardcoded file paths

Call combine/define_introns.py followed by combine/get_sjr.py to fill in exon detection data.

The combine directory contains several tools for visualizing expression levels in long introns.

## Splicing Rates.

1. Use combine/standard_table_reader.py to extract the set of recursive sites that you want to use
2. Run sequence/make_introns.py with the return statement uncommented. This merges recursive sites together into groups by intron.
3. Call rates/run_all.py with this file as an argument.
4. You can use plot.py with the summary table as an argument to plot the mean psi values
5. Use plot_transformed.py to plot coverage in transformed space (for QC)
