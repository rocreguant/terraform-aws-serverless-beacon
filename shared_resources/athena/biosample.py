import jsons
import boto3
import json
import pyorc
import os

from smart_open import open as sopen

from .common import AthenaModel


METADATA_BUCKET = os.environ['METADATA_BUCKET']
BIOSAMPLES_TABLE = os.environ['BIOSAMPLES_TABLE']

s3 = boto3.client('s3')
athena = boto3.client('athena')


class Biosample(jsons.JsonSerializable, AthenaModel):
    _table_name = BIOSAMPLES_TABLE
    # for saving to database order matter
    _table_columns = [
        'id',
        '_datasetId',
        '_cohortId',
        'individualId',
        'biosampleStatus',
        'collectionDate',
        'collectionMoment',
        'diagnosticMarkers',
        'histologicalDiagnosis',
        'measurements',
        'obtentionProcedure',
        'pathologicalStage',
        'pathologicalTnmFinding',
        'phenotypicFeatures',
        'sampleOriginDetail',
        'sampleOriginType',
        'sampleProcessing',
        'sampleStorage',
        'tumorGrade',
        'tumorProgression',
        'info',
        'notes'
    ]


    def __init__(
                self,
                *,
                id='',
                datasetId='',
                cohortId='',
                individualId='',
                biosampleStatus={},
                collectionDate=[],
                collectionMoment=[],
                diagnosticMarkers=[],
                histologicalDiagnosis=[],
                measurements=[],
                obtentionProcedure=[],
                pathologicalStage=[],
                pathologicalTnmFinding=[],
                phenotypicFeatures=[],
                sampleOriginDetail=[],
                sampleOriginType=[],
                sampleProcessing=[],
                sampleStorage=[],
                tumorGrade=[],
                tumorProgression=[],
                info=[],
                notes=[]
            ):
        self.id = id
        self._datasetId = datasetId
        self._cohortId = cohortId
        self.individualId = individualId
        self.biosampleStatus = biosampleStatus
        self.collectionDate = collectionDate
        self.collectionMoment = collectionMoment
        self.diagnosticMarkers = diagnosticMarkers
        self.histologicalDiagnosis = histologicalDiagnosis
        self.measurements = measurements
        self.obtentionProcedure = obtentionProcedure
        self.pathologicalStage = pathologicalStage
        self.pathologicalTnmFinding = pathologicalTnmFinding
        self.phenotypicFeatures = phenotypicFeatures
        self.sampleOriginDetail = sampleOriginDetail
        self.sampleOriginType = sampleOriginType
        self.sampleProcessing = sampleProcessing
        self.sampleStorage = sampleStorage
        self.tumorGrade = tumorGrade
        self.tumorProgression = tumorProgression
        self.info = info
        self.notes = notes


    def __eq__(self, other):
        return self.id == other.id


    @classmethod
    def parse_array(cls, array):
        biosamples = []
        var_list = list()
        case_map = { k.lower(): k for k in Biosample().__dict__.keys() }

        for attribute in array[0]['Data']:
            var_list.append(attribute['VarCharValue'])

        for item in array[1:]:
            biosample = Biosample()

            for attr, val in zip(var_list, item['Data']):
                try:
                    val = json.loads(val['VarCharValue'])
                except:
                    val = val.get('VarCharValue', '')
                biosample.__dict__[case_map[attr]] = val
            biosamples.append(biosample)

        return biosamples


    @classmethod
    def upload_array(cls, array):
        if len(array) == 0:
            return
        header = 'struct<' + ','.join([f'{col.lower()}:string' for col in cls._table_columns]) + '>'
        bloom_filter_columns = list(map(lambda x: x.lower(), cls._table_columns))
        key = f'{array[0].datasetId}-biosamples'
        
        with sopen(f's3://{METADATA_BUCKET}/biosamples/{key}', 'wb') as s3file:
            with pyorc.Writer(
                s3file, 
                header, 
                compression=pyorc.CompressionKind.SNAPPY, 
                compression_strategy=pyorc.CompressionStrategy.COMPRESSION,
                bloom_filter_columns=bloom_filter_columns) as writer:
                for biosample in array:
                    row = tuple(
                        biosample.__dict__[k] 
                        if type(biosample.__dict__[k]) == str
                        else json.dumps(biosample.__dict__[k])
                        for k in cls._table_columns
                    )
                    writer.write(row)


if __name__ == '__main__':
    pass