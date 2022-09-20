import random
import json
import os

from tqdm import tqdm
import pyorc
from smart_open import open as sopen

from athena.analysis import Analysis
from dynamodb.datasets import Dataset
from utils import get_samples


METADATA_BUCKET = os.environ['METADATA_BUCKET']


def get_radnom_analysis(id, datasetId, individualId, biosampleId, runId, seed=0):
    random.seed(seed)

    item = Analysis(id=id, datasetId=datasetId, individualId=individualId, biosampleId=biosampleId, runId=runId)
    item.aligner = random.choice(["bwa-0.7.8", "minimap2", "bowtie"])
    item.analysisDate = f"{random.randint(2018, 2022)}-{random.randint(1, 12)}-{random.randint(1, 28)}"
    item.pipelineName = f"pipeline {random.randint(1, 5)}"
    item.pipelineRef = "Example"
    item.variantCaller = random.choice(["GATK4.0", "SoapSNP", "kmer2snp"])

    return item


if __name__ == "__main__":
    header = 'struct<' + \
        ','.join([f'{col.lower()}:string' for col in Analysis._table_columns]) + '>'
    bloom_filter_columns = list(
        map(lambda x: x.lower(), Analysis._table_columns))
    # simlating 1 analysis per run
    for dataset in Dataset.scan():
        s3file = None
        writer = None
        id = dataset.id
        nosamples = dataset.sampleCount
        vcf = list(dataset.vcfLocations)[0]
        samples = get_samples(vcf)

        for itr, sample in tqdm(zip(range(nosamples), samples), total=nosamples):
            analysis = get_radnom_analysis(
                id=f'{id}-{itr}', datasetId=id, individualId=f'{id}-{itr}', biosampleId=f'{id}-{itr}', runId=f'{id}-{itr}', seed=f'{id}-{itr}')
            analysis.vcfSampleId = sample
            d_partition = f'datasetid={analysis.datasetId}'
            c_partition = f'cohortid={analysis.cohortId}'
            key = f'{analysis.datasetId}-analyses'

            if writer is None:
                s3file = sopen(
                    f's3://{METADATA_BUCKET}/analyses/{d_partition}/{c_partition}/{key}', 'wb')
                writer = pyorc.Writer(
                    s3file,
                    header,
                    compression=pyorc.CompressionKind.SNAPPY,
                    compression_strategy=pyorc.CompressionStrategy.COMPRESSION,
                    bloom_filter_columns=bloom_filter_columns
                )
            row = tuple(
                analysis.__dict__[k]
                if type(analysis.__dict__[k]) == str
                else json.dumps(analysis.__dict__[k])
                for k in Analysis._table_columns
            )
            writer.write(row)
        writer.close()
        s3file.close()

    # 1 million runs's analyses
    s3file = None
    writer = None
    id = '1M-people-sim'
    nosamples = 10**6

    for itr in tqdm(range(nosamples)):
        analysis = get_radnom_analysis(
            id=f'{id}-{itr}', datasetId=id, individualId=f'{id}-{itr}', biosampleId=f'{id}-{itr}', runId=f'{id}-{itr}', seed=f'{id}-{itr}')
        d_partition = f'datasetid={analysis.datasetId}'
        c_partition = f'cohortid={analysis.cohortId}'
        key = f'{analysis.datasetId}-analyses'

        if writer is None:
            s3file = sopen(
                f's3://{METADATA_BUCKET}/analyses/{d_partition}/{c_partition}/{key}', 'wb')
            writer = pyorc.Writer(
                s3file,
                header,
                compression=pyorc.CompressionKind.SNAPPY,
                compression_strategy=pyorc.CompressionStrategy.COMPRESSION,
                bloom_filter_columns=bloom_filter_columns
            )
        row = tuple(
            analysis.__dict__[k]
            if type(analysis.__dict__[k]) == str
            else json.dumps(analysis.__dict__[k])
            for k in Analysis._table_columns
        )
        writer.write(row)
    writer.close()
    s3file.close()
