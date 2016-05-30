# 1) intron file
# 2) exon file
# 3) BAM file
# 4) output directory
# 5) mean insert
# 6) stddev
# 7) read-len

rm -rf $4
mkdir $4

python paired_end.py $1 $2 $3 $4

echo 'wrote sam plus annotations'

# For some versions of samtools need to put "-o" in front of $4'/reads'
samtools view -bS $4'/reads.sam' | samtools sort - $4'/reads'

rm $4'/reads.sam'

echo 'sorted bam'

samtools index $4'/reads.bam' $4'/reads.bam.bai'

echo 'indexed bam'

index_gff --index $4'/annotations.gff' $4'/indexed/'

echo 'indexed annotations'

miso --run $4'/indexed/' $4'/reads.bam' --settings-filename miso_settings.txt --paired-end $5 $6 --read-len $7 --output-dir $4'/miso'

echo 'ran miso'

summarize_miso --summarize-samples $4'/miso' $4'/miso_summary'

echo 'summarized miso'
