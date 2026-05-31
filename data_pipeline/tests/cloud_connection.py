import os
from dotenv import load_dotenv
from google.cloud import storage


class connection_test:
    def __init__(self):
        load_dotenv()
        self.storage_client=storage.Client()
        self.bucket_name=os.getenv('BUCKET_NAME')
        self.bucket=self.storage_client.bucket(self.bucket_name)
    def list_buckets(self):
            
        buckets= self.storage_client.list_buckets()


        for bucket in buckets:
            print(f"Printing all available Buckets {bucket.name}")

    def create_file(self):
        
        file_name="test_file.txt"
        with open(file_name, "w") as f:
            f.write("Hello from Python!!!")
        return file_name
    
    def upload_blob(self):

        try:    
            blob=self.bucket.blob("tests")#set gcs file directory here m8
            file_name=self.create_file()

            #optional but it avoids race conditions and corruption when upload request is aborted.
            generation_match_condition=0
            #TODO check if file check found in gcs. 
            blob.upload_from_filename(file_name, if_generation_match=generation_match_condition)

            print(
                f"File {file_name} uploaded."
            )
            
        except Exception as e:
            print(f"An error as occurred: {e}")
    
if __name__=="__main__":
    connection=connection_test()
    connection.list_buckets()
    connection.upload_blob()