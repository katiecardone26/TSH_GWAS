# download gene locations and readme
wget http://ftp.ensembl.org/pub/release-115/gtf/homo_sapiens/Homo_sapiens.GRCh38.115.gtf.gz -P ensembl_start_stop_v115/
wget http://ftp.ensembl.org/pub/release-115/gtf/homo_sapiens/README -P ensembl_start_stop_v115/

# download refseq information
wget https://ftp.ensembl.org/pub/release-115/tsv/homo_sapiens/Homo_sapiens.GRCh38.115.refseq.tsv.gz -P ensembl_start_stop_v115/
wget https://ftp.ensembl.org/pub/release-115/tsv/homo_sapiens/README_refseq.tsv -P ensembl_start_stop_v115/

# convert to csv and remove comments
zcatensembl_start_stop_v115/Homo_sapiens.GRCh38.115.gtf.gz | grep -v '#!' | sed 's/\t/,/g' > ensembl_start_stop_v115/Homo_sapiens.GRCh38.115.gtf.csv

# call python script for cleaning
python clean_gtf.py \
    --coords ensembl_start_stop_v115/Homo_sapiens.GRCh38.115.gtf.csv \
    --ref ensembl_start_stop_v115/Homo_sapiens.GRCh38.115.refseq.tsv.gz \
    --output_prefix ensembl_start_stop_v115/Homo_sapiens.GRCh38.115
