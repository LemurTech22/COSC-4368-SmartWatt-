#used to upload data to GCS
#try to use 2 functions one to run and the other to set file pathing


def main(temp data)
    create var for file directory and names
        raw_energy_data
        raw_temperature_d
    upload_to_GCS(file_to_upload, title, filepath)
        connect to GCS
        combine file directory set them in parquet. 
        upload to GCS

# For Parquet (requires pyarrow):
# buffer = io.BytesIO()
# df.to_parquet(buffer, index=False)
# blob.upload_from_string(buffer.getvalue(), content_type='application/octet-stream')
