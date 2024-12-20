#!/bin/bash
# BSUB -J pheno-${pheno_id}
# BSUB -cwd _tmp/phenoplier/emerge
# BSUB -oo random_pheno${pheno_id}.%J.out
# BSUB -eo random_pheno${pheno_id}.%J.error
# -#BSUB -u miltondp@gmail.com
# -#BSUB -N
# BSUB -n 1
# BSUB -R "rusage[mem=3GB]"
# BSUB -M 3GB
# BSUB -W 10:00
# BSUB -R 'select[hname!=lambda25]'

# IMPORTANT: this is not a ready-for-submission script, it's a template.
#   see README.md to know how to generate the actual job scripts.

# make sure we use the number of CPUs specified
export n_jobs=1
export PHENOPLIER_N_JOBS=${n_jobs}
export NUMBA_NUM_THREADS=${n_jobs}
export MKL_NUM_THREADS=${n_jobs}
export OPEN_BLAS_NUM_THREADS=${n_jobs}
export NUMEXPR_NUM_THREADS=${n_jobs}
export OMP_NUM_THREADS=${n_jobs}

# Settings
COHORT_NAME="emerge"
REFERENCE_PANEL="gtex_v8"

# Paths
CODE_DIR=${PHENOPLIER_CODE_DIR}/nbs/15_gsa_gls/30-real_phenotypes
INPUT_SMULTIXCAN_DIR="${PHENOPLIER_EMERGE_SMULTIXCAN_DIR}"

OUTPUT_DIR="${PHENOPLIER_RESULTS_GLS}/${COHORT_NAME}/gls-${REFERENCE_PANEL}_mashr-sub_corr"
mkdir -p ${OUTPUT_DIR}

# Gene correlation matrix
#GENE_CORR_FILE="${PHENOPLIER_RESULTS_GLS}/gene_corrs/cohorts/${COHORT_NAME}/${REFERENCE_PANEL}/mashr/gene_corrs-symbols.per_lv/"
#GENE_CORR_FILE="${PHENOPLIER_RESULTS_GLS}/gene_corrs/cohorts/${COHORT_NAME}/${REFERENCE_PANEL}/mashr/gene_corrs-symbols-within_distance_10mb.per_lv/"
GENE_CORR_FILE="${PHENOPLIER_RESULTS_GLS}/gene_corrs/cohorts/${COHORT_NAME}/${REFERENCE_PANEL}/mashr/gene_corrs-symbols-within_distance_5mb.per_lv/"
#GENE_CORR_FILE="${PHENOPLIER_RESULTS_GLS}/gene_corrs/cohorts/${COHORT_NAME}/${REFERENCE_PANEL}/mashr/gene_corrs-symbols-within_distance_2mb.per_lv/"

bash ${CODE_DIR}/01_gls_phenoplier.sh \
  --input-file ${INPUT_SMULTIXCAN_DIR}/eMERGE_III_smultixcan_mashr_eqtl_EUR_${pheno_id}.txt \
  --gene-corr-file ${GENE_CORR_FILE} \
  --covars "gene_size gene_size_log gene_density gene_density_log" \
  --debug-use-sub-gene-corr 1 \
  --output-file ${OUTPUT_DIR}/gls_phenoplier-EUR_${pheno_id}.tsv.gz

