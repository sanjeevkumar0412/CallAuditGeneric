from app.model.start_transcribe import StartTranscribe


def main():
    try:
        transcribe_model = StartTranscribe()
        transcribe_model.start_transcribe_process()
    except Exception as e:
        print(f'caught {type(e)}: e', e)


if __name__ == '__main__':
    main()
