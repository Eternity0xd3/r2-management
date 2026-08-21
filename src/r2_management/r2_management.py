import os
from pathlib import Path

import boto3

class R2Management:
    def __init__(self, bucket_name, endpoint_url, access_key, secret_key, region_name='auto', public_url=None) -> None:
        self.bucket_name = bucket_name
        self.public_url = public_url
        self.s3 = boto3.client('s3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name
        )

    def is_object_exists(self, object_name) -> bool:
        return object_name in self.list()

    def upload(self, file_path, object_name) -> str:
        file_path = Path(file_path)
        if not file_path.is_file():
            raise ValueError("Path is not a file")
        self.s3.upload_file(str(file_path), self.bucket_name, object_name)
        if(self.public_url):
            return f"{self.public_url}/{object_name}"
        else:
            return f"{object_name}"

    def upload_multiple(self, file_paths, object_dir) -> list[str]:
        object_results = []
        object_dir = object_dir if object_dir.endswith("/") else object_dir + "/"
        for each_file in file_paths:
            file_name = Path(each_file).name
            object_name = object_dir + file_name 
            object_results.append(self.upload(each_file, object_name))
        return object_results

    def download(self, object_name, file_path) -> None:
        if not self.is_object_exists(object_name):
            raise ValueError("Object does not exist in bucket")
        self.s3.download_file(self.bucket_name, object_name, file_path)

    def list_objects(self) -> list[str]:
        response = self.s3.list_objects_v2(Bucket=self.bucket_name)
        objects = []
        while True:
            for obj in response.get('Contents', []):
                objects.append(obj)
            if response.get('IsTruncated'):
                response = self.s3.list_objects_v2(Bucket=self.bucket_name, ContinuationToken=response['NextContinuationToken'])
            else:
                break
        return objects

    def list(self) -> list[str]:
        return [obj['Key'] for obj in self.list_objects()]

    def delete(self, object_name) -> None:
        if not self.is_object_exists(object_name):
            raise ValueError("Object not found in bucket")
        self.s3.delete_object(Bucket=self.bucket_name, Key=object_name)