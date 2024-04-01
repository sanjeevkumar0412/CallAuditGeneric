from enum import Enum


class JobStatusEnum(Enum):
    Recording = 1
    Processing = 2
    CompletedTranscript = 3
    Failed = 4
    Draft = 5
    Exported = 6
    Starting = 7
    CompletedWithError = 8
    PreProcessing = 9
    SACompleted = 21
