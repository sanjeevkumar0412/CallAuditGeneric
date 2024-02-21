from app.utilities.utility import get_all_files,create_folder_structure

def build_transcribe_model(source_file_path,destination_path):
    try:
        print('source_file_path console :- ',source_file_path)
        print('destination_path console :- ',destination_path)
        file_collection = get_all_files(source_file_path)
        # model details, subscription
        create_folder_structure(file_collection,source_file_path,destination_path,True)
    except FileExistsError:   
        print('Error while creating build_transcribe_model')