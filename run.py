from app.model.start_transcribe import StartTranscribe
from app.services.logger_service import LoggerService


def main():
    try:
        logger_service = LoggerService()
        logger_service.info('asgsdhgfhsdg')
        transcribe_model = StartTranscribe()
        transcribe_model.start_transcribe_process()
    except Exception as e:
        print(f'caught {type(e)}: e', e)


if __name__ == '__main__':
    main()
