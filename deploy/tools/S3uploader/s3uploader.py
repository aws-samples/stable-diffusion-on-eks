import argparse
import boto3
import urllib3
import csv
from tqdm import tqdm
import os

# 初始化S3客户端
#session = boto3.Session(profile_name='ue1')
#s3 = session.client('s3')
s3 = boto3.client('s3')

# 读取CSV文件
def read_csv(csv_file):
    urls = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            urls.append(row)
    return urls

# 下载文件并上传到S3
def download_and_upload_to_s3(url, bucket, key, index, total):
    http = urllib3.PoolManager()
    response = http.request('GET', url, preload_content=False)

    total_size = int(response.headers['Content-Length'])
    chunk_size = 1024 * 1024  # 1 MB chunks (adjust as needed)
    
    # 使用 tqdm 创建下载进度条
    progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Downloading {url} ({index}/{total})")

    # 打开本地临时文件用于存储下载内容
    temp_file_path = '/tmp/temp_file'
    with open(temp_file_path, 'wb') as temp_file:
        for chunk in response.stream(chunk_size):
            temp_file.write(chunk)
            progress_bar.update(len(chunk))

    progress_bar.close()
    
    # 上传到S3并监控上传进度
    s3.upload_file(
        temp_file_path,
        bucket,
        key,
        Callback=ProgressPercentage(progress_bar, total_size)
    )
    
    os.remove(temp_file_path)  # 删除临时文件

    print(f"正在从 {url} 下载到S3{bucket}/{key} ({index}/{total})")

# 用于监控上传进度的回调函数
class ProgressPercentage:
    def __init__(self, progress_bar, total_size):
        self.progress_bar = progress_bar
        self.total_size = total_size
        self.uploaded = 0

    def __call__(self, bytes_amount):
        self.uploaded += bytes_amount
        self.progress_bar.update(bytes_amount)

def main(csv_file):
    # 读取CSV文件
    urls = read_csv(csv_file)
    total_files = len(urls)
    
    for index, row in enumerate(urls, start=1):
        url = row['url']
        bucket = row['bucket']
        key = row['key']
        
        try:
            download_and_upload_to_s3(url, bucket, key, index, total_files)
        except Exception as e:
            print(f"Failed to download and upload {url} to S3 bucket {bucket} with key {key}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download and upload files from a CSV to S3')
    parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    args = parser.parse_args()
    main(args.csv_file)
